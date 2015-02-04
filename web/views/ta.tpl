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
							<i class="i_title">[应用]:</i>{{viewmodel['audit_app']}}
						</li>
						<li class="clearfix">
							<div class="li_item"><i class="i_title">[下限值 ms]:</i><input type="text" id="low_times" class="inpt_txt" value="{{viewmodel['low_times']}}"/></div>
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
	                		<a href_url="/ta?audit_ip={{ip['audit_ip']}}&audit_app={{ip['audit_app']}}" class="ips" href="javascript:;">{{ip['audit_ip']}}({{ip['host_name']}})</a>
                %end
						</li>
					</ul>
				</div>
				<!--概览或明细-->
				<input type="hidden" id="time_type" value="{{viewmodel['timeType']}}"/>
				<!--页码-->
				<input type="hidden" id="cur_page" value="{{viewmodel['curpage']}}"/>
				<!--当前应用名称-->
                <input type="hidden" id="audit_app" value="{{viewmodel['audit_app']}}"/>
				<!--当前ip地址-->
			    <input type="hidden" id="audit_ip" value="{{viewmodel['audit_ip']}}"/>
				<!-- 最大页码 -->
				<input id="maxpage" value="{{viewmodel['maxpage']}}" type="hidden"/>
				<!--当前排序类型-->
				<input id="order_type" value="{{viewmodel['order_type']}}" type="hidden"/>
				<!--明细项获取url-->
                <input type="hidden" id="dispatcher" name="dispatcher" data-subItemsUrl="/subitems"/>

                <div id="treeMenu">
                    <div width="100%"  class="tr_tit" id="tr_tit">
                        <ul class="clearfix" href_url="/ta?">
                            <li class="h-32 col_2"><strong>请求路径(<font style="color:#f00;">{{viewmodel['audit_ip']}}</font>)</strong></li>
                            <li class="h-32 col_3">请求参数</li>
                            <li class="h-32 col_4" >请求次数</li>
                            <li class="h-32 col_5 sortCol" order_type="0"  title="按产生时间倒排"><span>请求时间</span><i class="d_icon"></i></li>
                            <li class="h-32 col_6 sortCol" order_type="1"  title="按消耗时间倒排"><span>请求耗时(ms)</span><i class="d_icon"></i></li>
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
					<div class="scott2" href_url="/ta?">
						<span>总计：{{viewmodel["rowcount"]}}条&nbsp;{{viewmodel['maxpage']}}页</span>
						<a page_index="{{viewmodel['prepage']}}" href="javascript:;" class="change_page">上一页</a>
						<span class="current">{{viewmodel['curpage']}}</span>
						<a page_index="{{viewmodel['afterpage']}}" href="javascript:;" class="change_page">下一页</a>
						<span>跳转第：</span>
						<input type="text" id="page" class="pageInput J_Number" maxlength="5">
						<span>页</span>
						<input type="button" id="pageSubmit" value="GO" class="go">
					</div>
				</div>
		</div>
		<div class="footer"></div>
		<script type="text/javascript" src="./static/js/sea.js" data-main="./static/js/tree" data-config="./static/js/config.js?v=1.0" id="seajsFile"></script>
	</body>
</html>