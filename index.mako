<html>

<h1>${thisdir}</h1>

% if subdirectories:
    <div id="links">
        <ul>
        % for subdir in subdirectories:
            <li><a href="${subdir}/index.html">${subdir}</a>
        % endfor
        </ul>
    </div>
% endif

% if image_fns:
    <div id="images">
        % for thumb, original in image_fns:
            <a href="${original}"><img src="${thumb}" /></a>
        % endfor
    </div>
% endif

</html>