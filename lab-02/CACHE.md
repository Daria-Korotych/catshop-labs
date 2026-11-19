# Cache · cold vs warm

Same commit (`65fe581`), `workflow_dispatch`, all caches deleted before the cold run.

| job | cold | warm |
|---|---|---|
| `test` (pip download cache, `actions/cache`) | 13s | 27s |
| `image` (BuildKit layers, `type=gha,mode=max`) | 1m 7s | 15s |
| whole run | 1m 23s | 44s |

The image build got faster: on the warm run 7 build steps came back `CACHED`, including `pip install` in the build stage, so only the cache export and the final image remained. `test` did not get faster: the pip cache was an exact hit (`Cache restored from key: pip-Linux-3.12-8f368dd…`), but the dependencies are a few MB, so the download it saves is smaller than the runner-to-runner noise in this job.

Runs: cold [44587142158](https://github.com/Daria-Korotych/catshop-labs/actions/runs/44587142158), warm [44587443810](https://github.com/Daria-Korotych/catshop-labs/actions/runs/44587443810).
