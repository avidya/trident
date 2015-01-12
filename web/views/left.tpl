<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title>menu</title>
    <link rel="stylesheet" type="text/css" href="./static/css/all.css">
</head>
<body>
<div class="left-header"><img src="/static/imgs/logo.png" alt="trident-manager"/><span style="width:70%;float:right;margin-top:5px;">trident-audit</span></div>
<div class="nav" style="margin-left:10px;">
    <h3 style="font-size: 16px;">应用列表：</h3>
    %for item in viewmodel:
    <ul>
        <li>&nbsp;</li>
    </ul>
    <ul>
        <li><a href="/content?app={{item['audit_app_encode']}}" target="showContent">{{item['audit_app']}}</a></li>
    </ul>
    %end
</div>
</body>
</html>