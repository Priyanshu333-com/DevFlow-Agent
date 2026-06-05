import gitlab
import os
from dotenv import load_dotenv

load_dotenv()

gl = gitlab.Gitlab(
    url=os.getenv('GITLAB_URL', 'https://gitlab.com'),
    private_token=os.getenv('GITLAB_TOKEN')
)

def get_user_projects():
    try:
        projects = gl.projects.list(owned=True, per_page=10)
        return [{"id": p.id, "name": p.name, "url": p.web_url} for p in projects]
    except Exception as e:
        return {"error": str(e)}

def get_failed_pipelines(project_id):
    try:
        project = gl.projects.get(project_id)
        pipelines = project.pipelines.list(status='failed', per_page=5)
        return [{"id": p.id, "status": p.status, "ref": p.ref} for p in pipelines]
    except Exception as e:
        return {"error": str(e)}

def get_pipeline_jobs(project_id, pipeline_id):
    try:
        project = gl.projects.get(project_id)
        pipeline = project.pipelines.get(pipeline_id)
        jobs = pipeline.jobs.list()
        failed_jobs = []
        for job in jobs:
            if job.status == 'failed':
                failed_jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "stage": job.stage,
                    "status": job.status
                })
        return failed_jobs
    except Exception as e:
        return {"error": str(e)}

def get_job_log(project_id, job_id):
    try:
        project = gl.projects.get(project_id)
        job = project.jobs.get(job_id)
        log = job.trace()
        return log.decode('utf-8')[-3000:] if isinstance(log, bytes) else str(log)[-3000:]
    except Exception as e:
        return {"error": str(e)}

def create_gitlab_issue(project_id, title, description):
    try:
        project = gl.projects.get(project_id)
        issue = project.issues.create({
            'title': title,
            'description': description,
            'labels': ['bug', 'ci-cd', 'auto-detected']
        })
        return {"issue_url": issue.web_url, "issue_id": issue.iid}
    except Exception as e:
        return {"error": str(e)}

def retry_pipeline(project_id, pipeline_id):
    try:
        project = gl.projects.get(project_id)
        pipeline = project.pipelines.get(pipeline_id)
        pipeline.retry()
        return {"message": "Pipeline retried successfully!"}
    except Exception as e:
        return {"error": str(e)}

def get_project_info(project_id):
    try:
        project = gl.projects.get(project_id)
        return {
            "name": project.name,
            "description": project.description,
            "url": project.web_url,
            "default_branch": project.default_branch
        }
    except Exception as e:
        return {"error": str(e)}