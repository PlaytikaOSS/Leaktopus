<template>
  <div class="scans">
    <ScansList />
  </div>
</template>

<script>
// @ is an alias to /src
import ScansList from '@/components/ScansList.vue'

export default {
  name: 'ScansView',
  components: {
    ScansList
  }
}
</script>
