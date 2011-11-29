<html>

<head>
<title>${thisdir}</title>
<style>
body {
     margin: 12px;
     font-family: Helvetica;
     font-weight: 300;
}
#links ul {
    list-style-type: square;
}
#links ul li {
    padding: 2px 0;
}
#images .imgwrapper {
    display: inline-block;
    text-align: center;
    padding: 8px 4px;
}
#images .img {
    width: ${thumb_width}px;
    padding-bottom: 4px;
}
#images .img img {
    max-width: ${thumb_width}px;
    max-height: ${thumb_width}px;
}

</style>
</head>

<body>

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
        % for basename, thumb, original in image_fns:
            <div class="imgwrapper">
                <div class="img"><a href="${original}"><img src="${thumb}" /></a></div>
                ${basename}
            </div>
        % endfor
    </div>
% endif

</body>
</html>
