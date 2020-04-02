from flask import render_template, request, session, url_for, redirect, make_response, send_file
from io import BytesIO
from . import main
from .validate import get_curator, get_image, crop_image, update_record
from .. import redis_client

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@main.route('/projects', methods=['GET'])
def projects():
    return render_template('projects.html')

@main.route('/validate/<project>', methods=['GET'])
def start_validation(project):
    if request.method == 'GET':
        if 'username' not in session:
            return redirect(url_for('.validation_login', project=project))
        stream_name = '%s_validation_work_stream' % project
        # first we check for any pending work
        pending_work = redis_client.xreadgroup('validation_workers', session['username'],
                                    {stream_name: '0'}, count=1)
        # comes down as [[<stream_name>, [work]]]
        pending_work = pending_work[0][1]
        if pending_work:
            work_id, work_def = pending_work[0]
            work_def = {
                k.decode('utf-8'): v.decode('utf-8') if type(v) == bytes else v
                for k, v in work_def.items()
            }
            
        else:
            new_work = redis_client.xreadgroup('validation_workers', session['username'],
                                                {stream_name: '>'}, count=1)
            return str(new_work)
        image_url = url_for('.image', project=project, upload_id=upload_id)
        image_url += '?' + '&'.join(['%s=%s' % (k, v) for k, v in bbox.items()])
        num_cols = 5
        other = []#sorted(other)
        rows = []
        for i in range(0, len(other), num_cols):
            rows.append(other[i:i+num_cols])
        other = rows
        return render_template('validate.html', project=project, 
                               upload_id=upload_id, image_url=image_url, 
                               top=top, other=sorted(other))

@main.route('/validate/<project>/login', methods=['GET', 'POST'])
def validation_login(project):
    if request.method == 'GET':
        message = session.get('login_message')
        if 'login_message' in session:
            del session['login_message']
        return render_template('validation_login.html', message=message)
    else:
        username = request.form['username'].strip().lower()
        if not username:
            session['login_message'] = 'Please specify a username'
            return redirect(url_for('.validation_login', project=project))
        session['username'] = username
        return redirect(url_for('.start_validation', project=project))
    

@main.route('/validate/<project>/<upload_id>-<detection_id>', methods=['GET', 'POST'])
def validate(project, upload_id, detection_id):
    if request.method == 'GET':
        curator = get_curator(project, session)
        after, before, top, other, bbox = curator.pull(session, upload_id, detection_id)
        image_url = url_for('.image', project=project, upload_id=upload_id)
        image_url += '?' + '&'.join(['%s=%s' % (k, v) for k, v in bbox.items()])
        if after[0] is not None:
            next_url = url_for('.validate', project=project, 
                                upload_id=after[0],
                                detection_id=after[1])
        else:
            next_url = None
        if before[0] is not None:
            last_url = url_for('.validate', project=project, 
                                upload_id=before[0],
                                detection_id=before[1])
        else:
            last_url = None
        num_cols = 5
        other = sorted(other)
        rows = []
        for i in range(0, len(other), num_cols):
            rows.append(other[i:i+num_cols])
        other = rows
        return render_template('validate.html', project=project, 
                               upload_id=upload_id, image_url=image_url,
                               next_url=next_url, last_url=last_url, top=top, 
                               other=sorted(other))
    elif request.method == 'POST':
        curator = get_curator(project, session)
        (next_upload_id, next_detection_id), *_ = curator.pull(session, upload_id, detection_id)
        if 'selection_from_top' in request.form:
            selection = request.form['selection_from_top']
        else:
            selection = request.form['selection_from_other']
        update_record(upload_id, detection_id, selection)
        if not next_upload_id:
            return redirect(url_for('.all_done', project=project))
        return redirect(url_for('.validate', project=project, 
                                upload_id=next_upload_id,
                                detection_id=next_detection_id))
    
@main.route('/validate/<project>/all_done', methods=['GET'])
def all_done(project):
    return render_template('all_done.html') 

@main.route('/image/<project>/<upload_id>', methods=['GET'])
def image(project, upload_id):
    upper = request.args.get('y1')
    lower = request.args.get('y0')
    left = request.args.get('x0')
    right = request.args.get('x1')
    image = get_image(upload_id)
    if None not in [upper, left, right, lower]:
        image = crop_image(image, float(left), float(upper), float(right), float(lower))
    return serve_pil_image(image)
