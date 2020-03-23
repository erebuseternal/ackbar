from flask import render_template, request, session, url_for, redirect, make_response
from . import main
from validate import create_curator, get_image, crop_image, update_record

@main.route('/validate/<project>/<upload_id>-<detection_id>', methods=['GET', 'POST'])
def validate(project, key):
    if request.method == 'GET':
        if 'validate' not in session:
            session['validate'] = {}
        curator = session['validate'].get(project)
        if curator is None:
            curator = create_curator(project, session)
            session['validate'][project] = curator
        after, before, top, other, bbox = curator.pull(session, upload_id, detection_id)
        image_url = url_for('.image', project=project, upload_id=upload_id)
        image_url += '?' + '&'.join(['%s=%s' % (k, v) for k, v in bbox.items()])
        if after[0] is not None:
            next_url = url_for('.validate', project=project, 
                                upload_id=after[0],
                                detection_id=after[1])
        else:
            next_url = None
        if before [0] is not None:
            last_url = url_for('.validate', project=project, 
                                upload_id=before[0],
                                detection_id=before[1])
        else:
            last_url = None
        return render_template('validate.html', project=project, 
                               upload_id=upload_id, image_url=image_url,
                               next_url=next_url, last_url=last_url, top=top, 
                               other=sorted(other))
    elif request.method == 'POST':
        curator = session['validate'][project]
        (next_upload_id, next_detection_id), *_ = curator.pull(session, upload_id, detection_id)
        if 'selection_from_top' in request.form:
            selection = request.form['selection_from_top']
        else:
            selection = request.form['selection_from_other']
        update_record(upload_id, detection_id, selection)
        return redirect(url_for('.validate', project=project, 
                                upload_id=next_upload_id,
                                detection_id=next_detection_id))

@main.route('/image/<project>/<upload_id>', methods=['GET'])
def image(project, upload_id):
    upper = request.args.get('y1')
    lower = request.args.get('y0')
    left = request.args.get('x0')
    right = request.args.get('x1')
    image = get_image(upload_id)
    if None not in [upper, left, right, lower]
        image = crop_image(image, left, upper, right, lower)
    response = make_response(image)
    response.content_type = 'image/jpg'
    return response
