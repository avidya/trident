/**
 * Created by wangyang on 2015/1/6.
 */
/**
 * 打印
 * @return {void}
 * @author wangyang
 * @version 2014-1-6
 * @since 2014-1-6
 */
define(function(require, exports, module) {
	var $dispatcher = $("#dispatcher");
	var reloadUrl = $dispatcher.attr('data-reloadUrl');
	var Util = require('util'), util = new Util();
	var DatePicker = require('datePicker'), dtPicker = new DatePicker();
	var Dialog = require('dialog'), dialog = new Dialog();
	require('formatdate');
/*	var sortUrl = $dispatcher.attr('data-sortUrl');
	var afterSort = $dispatcher.attr('data-afterUrl');*/

	var Main = {
		init : function() {
			Main.initLeftNav();
			Main.initPages();
			Main.pages();
		},
		initLeftNav : function() {
			var urlStatus = false;
			$('.leftNav li').each(function() {
				var me = $(this);
				var url = window.location.href;
				var loUrl = me.find('a').attr('href');
				if ((url + '/').indexOf(loUrl) > -1 && loUrl != '') {
					me.addClass('active').siblings('li').removeClass('active');
					urlStatus=true;
				} else {
					me.removeClass('active');
				}

			});
			if (!urlStatus) {
				$('.leftNav li').eq(0).addClass('active');
			}
		},
		initPages : function() {
			//时间空间面板切换
			$('body').delegate('#timeChange.normal', 'click', function() {
				var me = $(this);
				$('.timeDiv').toggle();
				me.text('[查看概览]');
				me.attr('class', 'li_btn changeBtn detail');
				$('#timeType').val('1');
			});
			$('body').delegate('#timeChange.detail', 'click', function() {
				var me = $(this);
				$('.timeDiv').toggle();
				me.text('[查看详细]');
				me.attr('class', 'li_btn changeBtn normal');
				$('#timeType').val('0');
			});
			//菜单展开收缩
			$('body').delegate('.jt', 'click', function() {
				var me=$(this);

				var finger_print = $(this).parent().parent().attr('data-id');
				var data_time = $("#createTime").val();
				var start_time = $("#startTime").val();
				var end_time = $("#endTime").val();
				var parent_order_nos = $(this).parent().parent().attr('parentordernos');
				var layer_no = parseInt($(this).parent().parent().attr('layerno'));
				var nodeIndex = parseInt($(this).parent().parent().attr('node-index'));
				var timeType = $("#timeType").val();
				var hasChild = $(this).parent().parent().parent().find('ul').length;
				if (hasChild == 0) {
					if (finger_print) {
						/*模拟请求数据 start*/
						/*var re = '<ul class="clearfix" node-index="10"><li data-id="327" style="text-indent:'+(nodeIndex+1)+'em'"><div class="col_0 col_item" ><a href="javascript:;" class="jt leaf"></a></div>' + '<div class="col_1 col_item">12123123</div><div class="col_2 col_item" ></div>' + '<div class="col_3 col_item">123123123真的吗真3真的吗真3真的吗真的吗真的啊</div><div class="col_4 col_item"></div><div class="col_5 col_item"><span class="proc-bar" style="width:20%"></span></div>' + '</li></ul>';
						$(this).parent().parent().after(re);
						$(this).attr('class', 'jt opened');*/
						/*模拟请求数据 end*/
						
						/*获取child*/
						$.get(reloadUrl, {
							parentordernos: parent_order_nos,
							fingerprint: finger_print,
							layerno: layer_no + 1,
							nodeIndex: nodeIndex + 1,
							timeType: timeType,
							data_time: data_time,
							end_time: end_time,
							start_time: start_time
						}, function(re) {
							me.parent().parent().after(re);
							me.attr('class', 'jt opened');
							//Main.initColor();
						}, 'html');
						/*获取child*/
					}
				} else {
					$(this).parent().parent().parent().find('ul').remove();
					$(this).attr('class', 'jt closed');
				}

			});

			$('body').delegate('.ips', 'click', function() {
				var load_url = $(this).attr('href_url') +"&end_time="+$("#endTime").val()+"&start_time="+$("#startTime").val()+"&timeType="+$("#timeType").val()+"&data_time="+$("#createTime").val();
				//alert(load_url);
				window.location = load_url;
			});

			//表格升序降序
			var upFlag = false;
			$('body').delegate('.sortCol', 'click', function() {
				var me = $(this);
				var orderType = me.attr('data-coltype');
				var en_app = $("#data_app").val();
				var ip_app = $("#data_ip").val();
				var sortCol = me.attr('data-colType');
				var load_url = "/ta?ip="+ ip_app+"&app="+en_app +"&end_time="+$("#endTime").val()+"&start_time="+$("#startTime").val()+"&timeType="+$("#timeType").val()+"&data_time="+$("#createTime").val()+"&orderType="+orderType;
				//alert(load_url);
				window.location = load_url;
				/*if (!upFlag) {
					Main.sortColumn(sortCol, !upFlag);
					//upFlag为是否为升序
					me.find('i').attr('class', 'u_icon');
					upFlag = true;
				} else {
					Main.sortColumn(sortCol, !upFlag);
					me.find('i').attr('class', 'd_icon');
					upFlag = false;
				}*/
			});

			//时间控件
			$("#createTime").on("click focus", function() {
				dtPicker.initByCfg({
					maxDate : $.formatDate(new Date(), 'yyyy-MM-dd'),
					dateFmt : 'yyyy-MM-dd'
				});
			});
			$("#startTime").on("click focus", function() {
				dtPicker.initByCfg({
					maxDate : $.formatDate(new Date(), 'yyyy-MM-dd'),
					dateFmt : 'yyyy-MM-dd HH:mm:ss'
				});
			});
			$("#endTime").on("click focus", function() {
				dtPicker.initByCfg({
					maxDate : $.formatDate(new Date(), 'yyyy-MM-dd'),
					dateFmt : 'yyyy-MM-dd HH:mm:ss'
				});
			});
		},

		/*sortColumn : function(sortCol, upFlag) {
			$.commonAjax({
				type : 'post',
				url : sortUrl,
				data : {
					sortCol : sortCol,
					upFlag : upFlag
				},
				success : function(re) {
					location.href = afterSort;
				},
				error : function(msg, status) {
					dialog.alert(msg);
				}
			});
		},*/

		initIcon : function() {
			var $jts = $('.jt');
			for (var i = 0; i < $jts.length; i++) {
				var $jt_itm = $($jts[i]);
				var isParent = $jt_itm.parent().parent().parent().find('ul').length;
				if (isParent == 0) {
					$jt_itm.attr('class', 'jt leaf');
				}
			}
		},

		// 处理分页页面跳转按钮
		pages : function() {
			$('#pageSubmit').click(function() {
				var pageIndexStr = $('#page').val();
				var maxNumber = $('#maxpage').val();
				var urlParams = $('#urlParams').val();
				var pageIndex = ~~pageIndexStr;
				if (pageIndexStr != pageIndex || pageIndexStr.indexOf(".") > -1) {
					alert('跳转页码必须为数值');
					$('#page').val("1");
					$('#page').focus();
					return false;
				} else if (pageIndex > ~~maxNumber) {
				    alert('跳转页码超过最大值，将查询最后一页：'+maxNumber);
					$('#page').val(maxNumber);
					pageIndex = ~~$('#page').val();//$('#page').focus();
					//return false;
				}
				if (pageIndex < 1) {
					pageIndex = 1;
				}
				window.location = "?page=" + pageIndex + urlParams;
			});
		},
        //处理缩进
        initColor : function(obj) {
            var $node_ul=obj.parents().find('.child_ul');
            for (var i = 0; i < $node_ul.length; i++) {
                var $node_item=$($node_ul[$node_ul.length-1]);
                var node_index = $node_item.attr('node-index');
                var node_color=$node_item.attr('node-color');
                $node_item.width($node_item.width()-2*node_index);
                $node_item.css('backgroundColor',node_color);
            }
        }

	};
	Main.init();
});
