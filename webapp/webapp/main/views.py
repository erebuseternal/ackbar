from flask import render_template, request, session, url_for, redirect, make_response, send_file
from io import BytesIO
from . import main
from .validate import get_curator, get_image, crop_image, update_record, get_class_names
from .. import redis_client

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@main.route('/projects', methods=['GET'])
def projects():
    return render_template('projects.html')

@main.route('/validate/<project>', methods=['GET', 'POST'])
def validate(project):
    stream_name = '%s_validation_work_stream' % project
    if request.method == 'GET':
        if 'username' not in session:
            return redirect(url_for('.validation_login', project=project))
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
            if not new_work:
                return redirect(url_for('.all_done', project=project))
            new_work = new_work[0][1]
            if new_work:
                work_id, work_def = new_work[0]
                work_def = {
                    k.decode('utf-8'): v.decode('utf-8') if type(v) == bytes else v
                    for k, v in work_def.items()
                }
        upload_id = work_def['upload_id']
        detection_id = work_def['detection_id']
        image_url = url_for('.image', project=project, upload_id=upload_id)
        image_url += '?' + '&'.join(['%s=%s' % (k, v) for k, v in work_def.items()
                                     if k in ('y0', 'y1', 'x0', 'x1')])
        top = [work_def[k] for k in ('c0', 'c1', 'c2', 'c3', 'c4')]
        num_cols = len(top)
        other = sorted([name for name in get_class_names(project)
                        if name not in top])
        rows = []
        for i in range(0, len(other), num_cols):
            rows.append(other[i:i+num_cols])
        other = rows
        return render_template('validate.html', project=project, 
                               upload_id=upload_id, image_url=image_url, 
                               top=top, other=other, stream_id=work_id.decode('utf-8'),
                               detection_id=detection_id)
    else:
        update_record(stream_name, request.form['stream_id'],
                      request.form['upload_id'], request.form['detection_id'],
                      request.form['selection'])
        return redirect(url_for('.validate', project=project))
        

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
        return redirect(url_for('.validate', project=project))
    
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
