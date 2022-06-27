<template>
    <div class="card mt-5">
        <div class="card-header bg-dark text-white">Initiate New Scan</div>
        <div class="card-body">
            <div class="alert alert-danger" role="alert" v-if="errors.length">
              <b>Please correct the following error(s):</b>
                <ul>
                    <li v-for="error in errors" :key="error">{{ error }}</li>
                </ul>
            </div>

            <form class="input-group">
                <div class="input-group mb-3">
                    <span class="input-group-text" title="E.g., domain.com">Search Query</span>
                    <input type="text" class="form-control"
                           aria-label="Search Query"
                           placeholder="domain.com"
                           required
                           v-model="search_query">
                   <input type="submit"
                        class="new-scan-submit btn btn-outline-primary"
                        :disabled="!search_query"
                        v-on:click="initNewScan"
                        value="Scan" />
                </div>
                <div class="accordion col-12" id="accordionPanelsStayOpenExample">
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="panelsStayOpen-headingOne">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#panelsStayOpen-collapseOne" aria-expanded="true" aria-controls="panelsStayOpen-collapseOne">
                                Advanced Search Options
                            </button>
                        </h2>
                        <div id="panelsStayOpen-collapseOne" class="accordion-collapse collapse show" aria-labelledby="panelsStayOpen-headingOne">
                            <div class="accordion-body">
                                <div class="input-group">
                                    <span class="input-group-text" title="Separated by comma (,)">Organization Domains</span>
                                    <input type="text" class="form-control"
                                        placeholder="domain.com, domain.net"
                                        aria-label="Organization domains"
                                        title="Separated by comma (,)"
                                        v-model="organization_domains">
                                    <span class="input-group-text" title="Separated by comma (,)">Sensitive Keywords</span>
                                    <input type="text" class="form-control"
                                        placeholder="canary-token, domain.internal"
                                        aria-label="Sensitive Keywords"
                                        title="Separated by comma (,)"
                                        v-model="sensitive_keywords">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <div class="scans-list card mt-5">
        <div class="card-header bg-dark text-white">Recent Scans</div>
        <div class="card-body">
            <button class="btn btn-primary mb-3" v-on:click="loadScans">
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" v-if="isRefreshing"></span>
                <font-awesome-icon icon="fa-solid fa-arrows-rotate" v-if="!isRefreshing" /> Refresh
            </button>
            <table class="table table-striped leaders-table">
                <thead>
                <th>ID</th>
                <th>Search Query</th>
                <th>Status</th>
                <th>Created At</th>
                <th>Completed At</th>
                <th>Actions</th>
                </thead>
                <tbody>
                  <tr v-for="scan in scans" :key="scan.scan_id" class="scan-item">
                      <td>{{ scan.scan_id }}</td>
                      <td>{{ scan.search_query }}</td>
                      <td>{{ scan.status_human }}</td>
                      <td>{{ scan.created_at }}</td>
                      <td>{{ scan.completed_at }}</td>
                      <td>
                          <button id="abort-scan" class="btn btn-secondary btn-warning"
                           v-on:click="abortScan(scan.scan_id)">Abort</button>
                          <button id="kill-scan" class="btn btn-secondary btn-danger ms-2"
                          title="Kills the scan in a ungraceful way"
                           v-on:click="killConfirm(scan.scan_id)">Kill</button>
                      </td>
                  </tr>
                </tbody>
            </table>
        </div>
    </div>

</template>

<script>
    import axios from 'axios'

    export default {
      name: 'ScansList',
      data() {
            return {
                scans: null,
                search_query: "",
                organization_domains: "",
                sensitive_keywords: "",
                isRefreshing: false,
                errors: []
            }
        },
       mounted() {
            this.loadScans()
        },
        methods: {
            checkForm: function () {
                this.errors = []
                let disallowed_chars = ["\u005e", "\u003b", "\u0026", "\u007c", "\u0022", "\u0060", "\u005c", "\u0021", "\u003c", "\u003e", "\u0024"]

                if (this.sensitive_keywords && disallowed_chars.some(v => this.sensitive_keywords.includes(v))) {
                    this.errors.push('The characters \u005e\u003b\u0026\u007c\u0022\u0060\u005c\u0021\u003c\u003e\u0024 are not allowed in the sensitive keywords field.');
                    return false
                }

                return true
            },
            killConfirm: function (scan_id) {
                if(confirm("Are you sure you want to kill the scan?")) {
                    let that = this
                    axios
                        .get(this.leaktopusApiUrl + 'api/scan/' + scan_id + '/kill')
                        .then(function () {
                            // Update the view.
                            that.loadScans()
                        })
                }
            },
            loadScans: function () {
                this.isRefreshing = true
                axios
                    .get(this.leaktopusApiUrl + 'api/scans')
                    .then(response => {
                        this.scans = response.data.results.reverse()
                        this.isRefreshing = false
                    })
            },
            initNewScan: function () {
                let that = this
                // Get the organization domains as array.
                const orgDomainsArray = this.organization_domains.split(/[, ]+/);
                const sensitiveKeywordsArray = this.sensitive_keywords.split(/[, ]+/);

                if (!this.checkForm())
                    return false

                axios
                    .post(this.leaktopusApiUrl + 'api/scan', {
                        "q": this.search_query,
                        "organization_domains": orgDomainsArray,
                        "sensitive_keywords": sensitiveKeywordsArray
                    })
                    .then(function () {
                        // Update the view.
                        that.loadScans()
                    })
                // Clean the search query model.
                that.search_query = ""
            },
            abortScan: function(scan_id) {
            let that = this
            axios
                .get(this.leaktopusApiUrl + 'api/scan/' + scan_id + '/abort')
                .then(function () {
                    // Update the view.
                    that.loadScans()
                })
            }
        }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
