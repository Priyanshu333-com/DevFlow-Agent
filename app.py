import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from gitlab_tools import (
    get_user_projects,
    get_failed_pipelines,
    get_pipeline_jobs,
    get_job_log,
    create_gitlab_issue,
    retry_pipeline,
    get_project_info
)

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
app = Flask(__name__)

def analyze_with_gemini(log_text, pipeline_info):
    prompt = f"""
    You are an expert DevOps engineer. Analyze this CI/CD pipeline failure.
    
    Pipeline Info: {json.dumps(pipeline_info)}
    Error Logs: {log_text}
    
    Provide:
    1. **Root Cause**: What exactly went wrong?
    2. **Fix Steps**: Step-by-step instructions to fix it
    3. **Issue Title**: Short title for GitLab issue (max 10 words)
    4. **Prevention**: How to prevent this in future
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-projects', methods=['GET'])
def get_projects():
    projects = get_user_projects()
    return jsonify(projects)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    project_id = data.get('project_id')
    if not project_id:
        return jsonify({"error": "Project ID is required"})
    project_info = get_project_info(project_id)
    if "error" in project_info:
        return jsonify({"error": f"Project not found: {project_info['error']}"})
    failed_pipelines = get_failed_pipelines(project_id)
    if isinstance(failed_pipelines, dict) and "error" in failed_pipelines:
        return jsonify({"error": failed_pipelines['error']})
    if not failed_pipelines:
        return jsonify({"message": "✅ No failed pipelines found!", "status": "success"})
    latest = failed_pipelines[0]
    jobs = get_pipeline_jobs(project_id, latest['id'])
    log_text = "No logs available"
    if jobs and not isinstance(jobs, dict):
        log_text = get_job_log(project_id, jobs[0]['id'])
    analysis = analyze_with_gemini(log_text, {
        "pipeline": latest,
        "project": project_info,
        "failed_jobs": jobs
    })
    return jsonify({
        "status": "failure_found",
        "project": project_info,
        "pipeline": latest,
        "failed_jobs": jobs,
        "analysis": analysis,
        "project_id": project_id,
        "pipeline_id": latest['id']
    })

@app.route('/create-issue', methods=['POST'])
def create_issue():
    data = request.json
    project_id = data.get('project_id')
    pipeline_id = data.get('pipeline_id')
    analysis = data.get('analysis')
    title = f"[Auto-Detected] Pipeline #{pipeline_id} CI/CD Failure"
    result = create_gitlab_issue(project_id, title, analysis)
    return jsonify(result)

@app.route('/retry-pipeline', methods=['POST'])
def retry():
    data = request.json
    project_id = data.get('project_id')
    pipeline_id = data.get('pipeline_id')
    result = retry_pipeline(project_id, pipeline_id)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)