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
	var $dispatcher = $("#dis");
	var Column = require('highCharts');
	var Util = require('util'), util = new Util();
	var getUrl = $dispatcher.attr('data-getUrl');
	var Main = {
		initColumn : function() {
			//左侧导航栏
			$('body').delegate('.leftNav li','click mouseover',function(){
				var me=$(this);
				me.addClass('active').siblings('li').removeClass('active');
			});
			//模式切换
			$('body').delegate('.act_title.now','click',function(){
				var me=$(this);
				me.siblings('.action_ul').find('.actionDate').toggle();
				me.text('[切换到详细模式]');
				me.attr('class','act_title history');
			});
			$('body').delegate('.act_title.history','click',function(){
				var me=$(this);
				me.siblings('.action_ul').find('.actionDate').toggle();
				me.text('[切换到历史模式]');
				me.attr('class','act_title now');
			});
			$.commonAjax({
				url : getUrl,
				dataType : "json",
				success : function(re) {
					for (var i = 0; i < re.length; i++) {
						var item = re[i];
						Column.initConfig($('#con' + (i + 1)), {
							title : item.title,
							subtitle : item.subtitle,
							categories : item.categories,
							yAxis_text : item.yAxis_text,
							seriesName : item.seriesName,
							seriesData : item.seriesData

						});
					}
				},
				error : function(xhr, textstatus) {
					alert(textstatus);
				}
			});
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
		init : function() {
			Main.initLeftNav();
			Main.initColumn();
		}
	};
	Main.init();
});
