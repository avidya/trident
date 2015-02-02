<!DOCTYPE  HTML>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<title>虚拟机状态监控</title>
		<link rel="stylesheet" type="text/css" href="./static/css/all2.css">
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
	                		<a href_url="/vm?ip={{ip['audit_ip_encode']}}&app={{ip['audit_app_encode']}}" class="ips" href="javascript:;">{{ip['audit_ip']}}({{ip['host_name']}})</a>
                %end
						</li>
					</ul>
				</div>
				<!--概览或明细-->
				<input type="hidden" id="time_type" value="{{viewmodel['timeType']}}"/>
				<!--当前应用名称-->
                <input type="hidden" id="app_encode" value="{{viewmodel['app_en']}}"/>
				<!--当前ip地址-->
			    <input type="hidden" id="ip_encode" value="{{viewmodel['ip_en']}}"/>

	<div class="actionArea clearfix">
		<input type="hidden" id="dispatcher" name="dispatcher" data-getUrl="/vm/status?ip={{viewmodel['ip_en']}}&app={{viewmodel['app_en']}}&type={{viewmodel['timeType']}}" />
		<a class="act_title now" id="changeTab" href="#">[切换到历史模式]</a>
		<div class="action_ul clearfix">
			<ul class="actionDate">
				<li class="remove">
					<a href="#">[-7d]</a>
				</li>
				<li class="remove">
					<a href="#">[-1d]</a>
				</li>
				<li class="remove">
					<a href="#">[-2h]</a>
				</li>
				<li class="remove">
					<a href="#">[-1h]</a>
				</li>
				<li class="add">
					<a href="#">[+1h]</a>
				</li>
				<li class="add">
					<a href="#">[+2h]</a>
				</li>
				<li class="add">
					<a href="#">[+1d]</a>
				</li>
				<li class="add">
					<a href="#">[+7d]</a>
				</li>
				<li class="now">
					<a href="#">[now]</a>
				</li>
			</ul>
			<ul class="actionDate" style="display: none">
				<li class="remove">
					<a href="#">[-7d]</a>
				</li>
				<li class="remove">
					<a href="#">[-1d]</a>
				</li>
				<li class="add">
					<a href="#">[+1d]</a>
				</li>
				<li class="add">
					<a href="#">[+7d]</a>
				</li>
				<li class="now">
					<a href="#">[now]</a>
				</li>
			</ul>
		</div>

	</div>
	<div id="coluArea" >
		<div class="clmItem" id="con1"></div>
		<div class="clmItem" id="con2">

		</div>
		<div class="clmItem ZW"></div>
		<div class="clmItem" id="con3">

		</div>
		<div class="clmItem" id="con4">

		</div>
		<div class="clmItem ZW"></div>
		<div class="clmItem" id="con5">

		</div>
		<div class="clmItem" id="con6">

		</div>
		<div class="clmItem" id="con7">

		</div>

	</div>
		</div>
		<div class="footer"></div>
		<script type="text/javascript" src="./static/js/sea.js" data-main="./static/js/column" data-config="./static/js/config.js?v=1.0" id="seajsFile"></script>
	</body>
</html>