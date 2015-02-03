<!DOCTYPE  HTML>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<title>虚拟机状态监控</title>
		<link rel="stylesheet" type="text/css" href="./static/css/all.css">
	</head>
	<body>
		<div id="header">
			<div class="box clearfix">
				<h1>通策集团</h1>
				<p class="title">TC-Cloud系统监控</p>
				<p class="mode">
                    <a href="/ta" >响应时间监控</a>
					<a href="/vm" class="nc">内存监控</a>
				</p>
			</div>
		</div>
		<div class="container clearfix">
			<div class="leftNav">
				<ul>
                    %for item in viewmodel["left"]:
                    <li>
						<a href="/ta?app={{item}}">{{item}}</a>
					</li>
                    %end
				</ul>
			</div>
			<div class="content">
				<div class="topMenu">
					<ul class="clearfix">
						<li>
							<i class="i_title">[应用]:</i>{{viewmodel['app']}}
						</li>
						<li class="clearfix">
							<div class="li_item timeDiv"
							%if int(viewmodel['timeType']) == 1:
								style="display:none;"
							%end	
							">
								<i class="i_title">[查询日期]:</i>
								<input type="text" class="inpt_txt Wdate" id="createTime" value="{{viewmodel['data_time']}}"/>
							</div>
							<div class="fl timeDiv" 
							%if int(viewmodel['timeType']) == 0:
								style="display:none;"
							%end								
							>
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
								%if int(viewmodel['timeType']) == 1:
								<a class="li_btn changeBtn detail" href="javascript:;" id="timeChange">[查看概览]</a>
								%else:
								<a class="li_btn changeBtn normal" href="javascript:;" id="timeChange">[查看详细]</a>
								%end
							</div>
						</li>
						<li class="li_ip">
                            <i class="i_title">[hosts]:</i>
                %for ip in viewmodel["apps"]:
	                		<a href_url="/vm?ip={{ip['audit_ip']}}&app={{ip['audit_app']}}" class="ips" href="javascript:;">{{ip['audit_ip']}}({{ip['host_name']}})</a>
                %end
						</li>
					</ul>
				</div>
				<!--概览或明细-->
				<input type="hidden" id="time_type" value="{{viewmodel['timeType']}}"/>
				<!--当前应用名称-->
                <input type="hidden" id="app" value="{{viewmodel['app']}}"/>
				<!--当前ip地址-->
			    <input type="hidden" id="ip" value="{{viewmodel['ip']}}"/>

	<div class="actionArea clearfix">
		<input type="hidden" id="dispatcher" name="dispatcher" page-getUrl="/vm" data-getUrl="/vm/status?ip={{viewmodel['ip']}}&app={{viewmodel['app']}}" />
		<a class="act_title now" id="changeTab" href="#">[切换到历史模式]</a>
		<div class="action_ul clearfix">
			<ul class="actionDate">
				<li class="remove">
					<a class="timeShift" time_shift="-604800" href="javascript:;">[-7d]</a>
				</li>
				<li class="remove">
					<a class="timeShift" time_shift="-86400" href="javascript:;">[-1d]</a>
				</li>
				<li class="remove">
					<a class="timeShift" time_shift="-7200" href="javascript:;">[-2h]</a>
				</li>
				<li class="remove">
					<a class="timeShift" time_shift="-3600" href="javascript:;">[-1h]</a>
				</li>
				<li class="add">
					<a class="timeShift" time_shift="3600" href="javascript:;">[+1h]</a>
				</li>
				<li class="add">
					<a class="timeShift" time_shift="7200" href="javascript:;">[+2h]</a>
				</li>
				<li class="oneDayAfter">
					<a class="timeShift" time_shift="86400" href="javascript:;">[+1d]</a>
				</li>
				<li class="sevenDaysAfter">
					<a class="timeShift" time_shift="604800" href="javascript:;">[+7d]</a>
				</li>
				<li class="now">
					<a class="timeShift" time_shift="0" href="now">[now]</a>
				</li>
			</ul>
			<ul class="actionDate" style="display: none">
				<li class="remove">
					<a class="timeShift" time_shift="-604800" href="javascript:;">[-7d]</a>
				</li>
				<li class="remove">
					<a class="timeShift" time_shift="-86400" href="javascript:;">[-1d]</a>
				</li>
				<li class="add">
					<a class="timeShift" time_shift="86400" href="javascript:;">[+1d]</a>
				</li>
				<li class="add">
					<a class="timeShift" time_shift="604800" href="javascript:;">[+7d]</a>
				</li>
				<li class="now">
					<a class="timeShift" time_shift="0" href="now">[now]</a>
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