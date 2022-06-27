<template>
    <h2>GitHub Preferences</h2>
    <div class="card mt-5">
        <div class="card-header bg-dark text-white">Add New Repository Ignore Pattern</div>
        <div class="card-body">
            <div class="input-group">
                <span class="input-group-text">Pattern</span>
                <input type="text" class="form-control"
                       placeholder="^https://github.com/OWNER/REPO"
                       id="ignored_pattern"
                       name="ignored_pattern"
                       required
                       v-model="new_ignore_pattern">
               <button class="add-ignore-submit btn btn-outline-secondary" :disabled="!new_ignore_pattern" v-on:click="addIgnoredPattern">Ignore Pattern</button>
            </div>
        </div>
    </div>

    <div class="card mt-5">
        <div class="card-header bg-dark text-white">Ignored Repository Patterns</div>
        <div class="card-body">
            <table class="table table-striped leaders-table">
                <thead>
                <th>ID</th>
                <th>Pattern</th>
                <th>Actions</th>
                </thead>
                <tbody>
                  <tr v-for="ignore in github_ignored" :key="ignore.id" class="ignore-item">
                      <td>{{ ignore.id }}</td>
                      <td>{{ ignore.pattern }}</td>
                      <td>
                          <button id="delete-ignored" class="btn btn-secondary btn-danger" v-on:click="deleteIgnoredPattern(ignore.id)">Delete</button>
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
  name: 'GithubPrefs',
  data() {
        return {
            github_ignored: null,
            leakcontent: null,
            new_ignore_pattern: ''
        }
    },
   mounted() {
        axios
            .get(this.leaktopusApiUrl + 'api/preferences/github')
            .then(response => (this.githubIgnoredLoaded(response)))
    },
    methods: {
        githubIgnoredLoaded: function (data) {
            this.github_ignored = data.data.results.ignored_repos
        },
        addIgnoredPattern: function() {
            let that = this
            // Send the add request.
            const config = {
                method: 'put',
                url: this.leaktopusApiUrl + 'api/preferences/github',
                headers: {
                    'Content-Type': 'application/json'
                },
                data : {
                    pattern: this.new_ignore_pattern
                }
            };
            axios(config)
                .then(function(data) {
                    // Update the view.
                    that.new_ignore_pattern = ''
                    that.github_ignored = data.data.results.ignored_repos
                })
        },
        deleteIgnoredPattern: function(pattern_id) {
            let that = this
            // Send the delete request.
            const config = {
                method: 'delete',
                url: this.leaktopusApiUrl + 'api/preferences/github',
                headers: {
                    'Content-Type': 'application/json'
                },
                data : {
                    id: pattern_id
                }
            };
            axios(config)
                .then(function (data) {
                    // Update the view.
                    that.github_ignored = data.data.results.ignored_repos
                })
        }
    }
}
</script>
