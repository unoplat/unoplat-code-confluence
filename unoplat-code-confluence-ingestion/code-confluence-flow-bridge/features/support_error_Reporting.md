# Objective 

We would want to track in progress workflows be it parent and child with proper status and in event of error the user will be present in frontend with error report which he can submit to our github repo as a issue and can track it directly in our application.

## Context

We have a interceptor class for temporal called parent_workflow_interceptor.

The argument it receives is repoworkflowenvelope. it includes all information regarding repository and its codebases which should be filled in respective tables first that is repository and codebase config inside repository_data.

Then we should fill in repositoryworkflowrun  with the right details.

Then we update it if result = await self.next.execute_workflow(input) this goes well then we just have to update the status of entire workflow that is parent workflow as completed.

Also in case of error be it any activity error , childworkflow error,application error  we have to fill in error report and update the repository workflow run with the error report and also the status update.

