<!DOCTYPE  HTML>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<title>响应时间监控</title>
		<link rel="stylesheet" type="text/css" href="./static/css/all.css">
	</head>
	<body>
		<div id="header">
			<div class="box clearfix">
				<h1>通策集团</h1>
				<p class="title">TC-Cloud系统监控</p>
				<p class="mode">
                    <a href="/ta" >响应时间监控</a>
					<a href="#" class="nc">内存监控</a>
				</p>
			</div>
		</div>
		<div class="container clearfix">
			<div class="leftNav">
				<ul>
                    %for item in viewmodel["left"]:
                    <li>
						<a href="/ta?app={{item['audit_app_encode']}}">{{item['audit_app']}}</a>
					</li>
                    %end
				</ul>
			</div>
			<div class="content">
				<div class="topMenu">
					<ul class="clearfix">
						<li>
							<i class="i_title">[应用]:</i>{{viewmodel['app_name']}}
						</li>
						<input type="hidden" id="timeType" value="0"/>
						<li class="clearfix">
							<div class="li_item timeDiv">
								<i class="i_title">[查询日期]:</i>
								<input type="text" class="inpt_txt Wdate" id="createTime" value="{{viewmodel['data_time']}}"/>
							</div>
							<div class="fl timeDiv" style="display:none;">
								<div class="li_item">
									<i class="i_title">[开始时间]:</i>
									<input type="text" class="inpt_txt Wdate" id="startTime" value="{{viewmodel['start_time']}}"/>
								</div>
								<div class="li_item">
									<i class="i_title">[结束时间]:</i>
									<input type="text" class="inpt_txt Wdate" id="endTime" value="{{viewmodel['end_time']}}"/>
								</div>
							</div>
							<div class="li_item">
								<a class="li_btn changeBtn normal" href="javascript:;" id="timeChange">[查看详细]</a>
							</div>
						</li>
						<li class="li_ip">
                            <i class="i_title">[hosts]:</i>
                %for ip in viewmodel["ips"]:
	                		<a href_url="/ta?ip={{ip['audit_ip_encode']}}&app={{ip['audit_app_encode']}}" class="ips" href="javascript:;">{{ip['audit_ip']}}({{ip['host_name']}})</a>
                %end
						</li>
					</ul>
				</div>
                <input type="hidden" id="data_app" value="{{viewmodel['app_en']}}"/>
			    <input type="hidden" id="data_ip" value="{{viewmodel['ip_en']}}"/>
                <input type="hidden" id="dispatcher" name="dispatcher" data-reloadUrl="/subitems"/>
                <div id="treeMenu">
                    <div width="100%"  class="tr_tit" id="tr_tit">
                        <ul class="clearfix">
                            <li class="h-32 col_2"><strong>url(<font style="color:#f00;">{{viewmodel['ip_address']}}</font>)</strong></li>
                            <li class="h-32 col_3">attachments</li>
                            <li class="h-32 col_4" >times</li>
                            <li class="h-32 col_5 sortCol" data-coltype="0"  title="按产生时间倒排"><span>create time</span><i class="d_icon"></i></li>
                            <li class="h-32 col_6 sortCol" data-coltype="1"  title="按消耗时间倒排"><span>avg-elapse(ms)</span><i class="d_icon"></i></li>
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
			    </div>
                <div class="pager">
					<div class="scott2">
						<span>总计：{{viewmodel["rowcount"]}}条&nbsp;&nbsp;&nbsp;</span>

						<a href="?page={{viewmodel['prepage']}}&ip={{viewmodel['ip_en']}}&app={{viewmodel['app_en']}}&data_time={{viewmodel['data_time']}}&timeType=0">上一页</a>

						<span class="current">{{viewmodel['curpage']}}</span>

						<a href="?page={{viewmodel['afterpage']}}&ip={{viewmodel['ip_en']}}&app={{viewmodel['app_en']}}&data_time={{viewmodel['data_time']}}&timeType=0">下一页</a>

						<span>跳转第：</span>
						<input type="text" id="page" class="pageInput J_Number" maxlength="5">
						<span>页</span>
						<input type="button" id="pageSubmit" value="GO" class="go">
						<input id="maxpage" value="{{viewmodel['maxpage']}}" type="hidden">
						<input id="urlParams" value="" type="hidden">
					</div>
				</div>
		</div>
		<div class="footer"></div>
		<script type="text/javascript" src="./static/js/sea.js" data-main="./static/js/tree" data-config="./static/js/config.js?v=1.0" id="seajsFile"></script>
	</body>
</html>