#!/usr/bin/env python3
# app.py
from bottle import Bottle, request, response, run
import json
from datetime import datetime

app = Bottle()

def _params_to_dict(params):
    out = {}
    for k in params:
        vals = params.getall(k)
        out[k] = vals if len(vals) > 1 else vals[0]
    return out

@app.route('/debug', method=['GET','POST','PUT','PATCH','DELETE','OPTIONS'])
def debug():
    # Try JSON first
    try:
        json_body = request.json
    except Exception:
        json_body = None

    form  = _params_to_dict(request.forms) if request.forms else {}
    query = _params_to_dict(request.query) if request.query else {}

    # Collect uploaded files (names only, not content)
    files = []
    for field in request.files.keys():
        for f in request.files.getall(field):
            files.append({
                "field": field,
                "filename": f.filename,
                "content_type": f.content_type,
                "size": getattr(f, 'content_length', None)
            })

    # Provide a small raw body preview when not JSON/form
    raw_preview = None
    if json_body is None and not form and request.content_length:
        try:
            raw_bytes = request.body.read()
            request.body.seek(0)  # rewind so other code (if any) can still read
            raw_preview = raw_bytes[:2048].decode('utf-8', errors='replace')
        except Exception:
            raw_preview = "<unreadable>"

    payload = {
        "when": datetime.utcnow().isoformat() + "Z",
        "request": {
            "method": request.method,
            "url": request.url,
            "path": request.path,
            "client_ip": request.remote_addr,
            "headers": dict(request.headers),
            "cookies": dict(request.cookies) if request.cookies else {},
            "query": query,
            "form": form,
            "json": json_body,
            "files": files,
            "content_type": request.get_header('Content-Type'),
            "content_length": request.content_length,
            "raw_body_preview": raw_preview
        }
    }
    response.content_type = 'application/json'
    return json.dumps(payload, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8080, debug=True, reloader=True)
