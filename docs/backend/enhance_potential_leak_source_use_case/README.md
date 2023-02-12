# Documentation for enhance_potential_leak_source_use_case.py

## Cases
- PLS scanned for the first time.
- PLS found again on an n+ scan.
  - PLS acknowledged.
  - PLS not acknowledged.
    - PLS wasn't modified since previous run.
    - PLS modified since previous run.
    - New enhancement modules have been added since the previous scan.
- PLS found again, but for a different search query.

## Highlights
- In the case of same PLS found from a different search query - 
  run again all modules for the found PLS, due to the expected low number of such cases.

## Diagram

```mermaid
  flowchart TD
    PLSScanDone((PLS Scan Completed.<br>Enhance PLS)) --> GL(Get leak by search query, leak URL and not acknowledged.)
    GL --> ILE{Is leak exists?}
    ILE -->|No| DN((Do nothing.))
    ILE --> LEI{Is module executed for leak?\nBy leak URL, search query and module key.}
    subgraph Iterate over all enhancement modules
      LEI -->|Yes| LEDE{PLS modified since last execution?}
      LEI -->|No| LDE1(Upsert the execution status in DB.)
      LDE1 --> LDE2(Execute enhancement task.)
      LEDE -->|Yes| LDE1    
    end
      LEDE -->|No| DN
```
