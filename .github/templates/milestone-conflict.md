🚩 **Milestone Conflict Detected**

The PR and the linked issue have **different milestones** assigned. Only one can be kept.

**Current State:**
- **PR Milestone:** [{PR_MILESTONE_NAME}]({PR_MILESTONE_URL}) (#{PR_MILESTONE_NUM})
- **Issue Milestone:** [{ISSUE_MILESTONE_NAME}]({ISSUE_MILESTONE_URL}) (#{ISSUE_MILESTONE_NUM})
- **Linked Issue:** [#{ISSUE_NUM}]({ISSUE_URL})

**What Happened:**
The auto-labeling workflow detected that PR #{PR_NUM} and issue #{ISSUE_NUM} have conflicting milestones. This must be resolved manually before this PR can be merged.

**How to Resolve:**

1. Decide which milestone should be correct:
   - Use [`{PR_MILESTONE_NAME}`]({PR_MILESTONE_URL}) for this PR/issue?
   - Use [`{ISSUE_MILESTONE_NAME}`]({ISSUE_MILESTONE_URL}) for this PR/issue?

2. Update the milestone in either the PR or issue to match the other

3. Push an empty commit to trigger the workflow again:
   ```bash
   git commit --allow-empty -m "ci: resolve milestone conflict in #{PR_NUM}"
   git push
   ```

4. The workflow will re-run and verify the conflict is resolved

**Need Help?**
- [View Milestones]({MILESTONES_URL})

---
_This check was performed by the auto-labeling workflow._
