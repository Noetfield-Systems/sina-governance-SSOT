# NOOS instruction — install compute ROI authority pointer (SG PR #62)

**decision_id:** `NF-COMPUTE-ROI-ALLOCATION-V1`  
**PR:** https://github.com/Noetfield-Systems/sina-governance-SSOT/pull/62  
**candidate_sha:** `8ce1e22ac1354dff33254c0d6742d3499250ce45`  
**merge_strategy:** merge_commit after green CI

1. After SG PR #62 merges to `main`, re-read SG `main` and set `sg_authority_sha` to that merge commit (must be ancestor of `main`).
2. Install `data/sg-authority-ref-compute-roi-v1.json` from SG (copy verbatim).
3. Do not redefine platform allocation in NOOS docs; cite SG paths only.
4. Route GHA / Actions spend under classes A–D; product wake stays Cloudflare `job_id` HTTP.
5. HOLD preserved — pointer install ≠ promote.
