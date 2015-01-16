<!DOCTYPE  HTML>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<title>pview</title>
		<link rel="stylesheet" type="text/css" href="./static/css/all.css">
	</head>
	<body>
		<div class="header"></div>
		<div class="container">
			<div class="clearfix" style="font-size: 18px;"><p style="font-size: 20px; "><strong>application:&nbsp;</strong>{{viewmodel['app_name']}}</p>
				<p>&nbsp;</p>
				<p><strong>create date:&nbsp;</strong><input type="text" value="{{viewmodel['data_time']}}" id="data_time" style="border: #f00 1px solid;width:70px;height:25px;"/></p>
				<strong>hosts:</strong>
%for ip in viewmodel["ips"]:
			<a href_url="/content?ip={{ip['audit_ip_encode']}}&app={{ip['audit_app_encode']}}" class="ips" href="javascript:;">{{ip['audit_ip']}}</a>;
%end
							<p>&nbsp;</p>
		</div>
			<input type="hidden" id="data_app" value="{{viewmodel['app_en']}}"/>
			<input type="hidden" id="data_ip" value="{{viewmodel['ip_en']}}"/>
			<input type="hidden" id="dispatcher" name="dispatcher" data-reloadUrl="/subitems"/>
			<div id="treeMenu">
				<div width="100%"  class="tr_tit" id="tr_tit">
					<ul class="clearfix">
						<li class="h-32 col_2"><strong>url(<font style="color:#f00;">{{viewmodel['ip_address']}}</font>)</strong></li>
						<li class="h-32 col_3">attachments</li>
						<li class="h-32 col_4">times</li>
						<li class="h-32 col_5">create time</li>
						<li class="h-32 col_6">avg-elapse(ms)</li>
					</ul>
				</div>
%for item in viewmodel["rows"]:
				<ul class="tree_content clearfix ul_bg">
					<li data-id="{{item['finger_print']}}" layerno="0" parentordernos="0" class="clearfix" node-index="0">
						<div class="col_2 col_item" title="{{item['url']}}" ><a href="javascript:;" class="jt closed"></a>{{item['url']}}</div>
						<div class="col_3 col_item" title="{{item['finger_print']}}">&nbsp;</div>
						<div class="col_4 col_item">{{item['times']}}</div>
						<div class="col_5 col_item">{{item['create_time']}}</div>
						<div class="col_6 col_item"><div class="bar_warp"><span class="proc-bar" style="width:{{item['elapse_bar']}}%;"></span></div><i class="pro_i">{{item['elapse']}}</i></div>
					</li>
				</ul>
%end

				<div class="pager">
					<div class="scott2">

						<span>总计：{{viewmodel["rowcount"]}}条&nbsp;&nbsp;&nbsp;</span>

						<a href="?page={{viewmodel['prepage']}}&ip={{viewmodel['ip_en']}}&app={{viewmodel['app_en']}}&qtime={{viewmodel['data_time']}}">上一页</a>

						<span class="current">{{viewmodel['curpage']}}</span>

						<a href="?page={{viewmodel['afterpage']}}&ip={{viewmodel['ip_en']}}&app={{viewmodel['app_en']}}&qtime={{viewmodel['data_time']}}">下一页</a>

						<span>跳转第：</span>
						<input type="text" id="page" class="pageInput J_Number" maxlength="5">
						<span>页</span>
						<input type="button" id="pageSubmit" value="GO" class="go">
						<input id="maxpage" value="{{viewmodel['maxpage']}}" type="hidden">
						<input id="urlParams" value="" type="hidden">

					</div>
				</div>

			</div>

		</div>
		<div class="footer"></div>
		<script type="text/javascript" src="./static/js/sea.js" data-main="./static/js/tree" data-config="./static/js/config.js?v=1.0" id="seajsFile"></script>
	</body>
</html>