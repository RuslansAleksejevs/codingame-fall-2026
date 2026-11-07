#!/usr/bin/env python3
"""Task-scoped JSON-lines API client; OAuth credentials stay in process memory."""
import json
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

BASE = Path(__file__).resolve().parents[2]
API = 'https://www.codingame.com/api/v1'
CHALLENGE = '/challenges/fall-challenge-2026'
token = None
device = None


def call(method, path, body=None, authenticated=True):
    headers = {'Content-Type': 'application/json', 'Accept-Language': 'en'}
    if authenticated:
        assert token, 'Authentication required'
        headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request(API + path, data=None if body is None else json.dumps(body).encode(), headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=50) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def sanitized(value):
    if isinstance(value, dict):
        return {k: sanitized(v) for k, v in value.items() if k not in ('access_token', 'device_code', 'email', 'registration_form')}
    if isinstance(value, list):
        return [sanitized(x) for x in value]
    if isinstance(value, str):
        return re.sub(r'cgp_[A-Za-z0-9]{42}', '[REDACTED]', value).replace(str(BASE), '${PROJECT_ROOT}')
    return value


print(json.dumps({'ready': True, 'credential_storage': 'process memory only'}), flush=True)
for line in sys.stdin:
    try:
        command = json.loads(line)
        op = command.get('op', 'request')
        if op == 'exit':
            break
        if op == 'auth_start':
            assert device is None and token is None, 'An authorization flow already exists'
            status, device = call('POST', '/auth/device', {'client_name': 'Codex - Fall Challenge 2026', 'scope': 'challenge:read challenge:play challenge:submit'}, False)
            result = {k: device[k] for k in ('user_code', 'verification_uri_complete', 'interval', 'expires_in') if k in device}
        elif op == 'auth_poll':
            assert device and not token
            status, data = call('POST', '/auth/token', {'grant_type': 'urn:ietf:params:oauth:grant-type:device_code', 'device_code': device['device_code']}, False)
            if 'access_token' in data:
                token = data['access_token']
                device = None
                result = {'authenticated': True, 'scope': data.get('scope'), 'expires_at': data.get('expires_at')}
            else:
                result = sanitized(data)
        else:
            path = command['path']
            assert path.startswith(CHALLENGE) or re.fullmatch(r'/test-games/\d+(\?[^\s]*)?|/games/\d+(\?[^\s]*)?|/me|/limits\?challenge=fall-challenge-2026', path)
            method = command.get('method', 'GET')
            assert method == 'GET' or method == 'POST' and path.split('?')[0] in (CHALLENGE + '/test-games', CHALLENGE + '/submissions')
            body = command.get('body')
            if 'code_file' in command:
                body = dict(body or {}, code=(BASE / command['code_file']).read_text())
            status, data = call(method, path, body)
            result = sanitized(data)
            if 'save' in command:
                destination = (BASE / command['save']).resolve()
                assert destination.is_relative_to(BASE / 'experiments')
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(json.dumps(result, indent=2) + '\n')
            if 'keys' in command:
                result = {k: result[k] for k in command['keys'] if k in result}
        print(json.dumps({'http_status': status, 'result': result}), flush=True)
    except Exception as error:
        print(json.dumps({'client_error': type(error).__name__, 'message': sanitized(str(error))}), flush=True)
