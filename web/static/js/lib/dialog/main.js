/**
 * 定义artDialog的接口
 * User: 张顺金 <zhangshunjin@eetop.com>
 * Date: 13-4-8 上午11:20
 */
define(function(require, exports, module) {

    require('lib/dialog/src/artDialog/skins/black.css');
    require('lib/dialog/src/artDialog/jquery.artDialog');
    require('dialogTools');

    var getStaticPath = function() {
        var $tar = $('#seajsFile');
        if ($tar.length) {
            var src = $tar.attr('src');
            src = src.split('js/');
            return src[0];
        }
    };
    var skinPath = getStaticPath() + 'js/lib/dialog/src/artDialog';

    function Dialog() {}

    /**
     * @description: Popup Dialog
     * @example：new Dialog().init({ lock: true, background: '#000', opacity: 0.75, title: '确认', content: document.getElementById('Policy'), cancelVal: '关闭', cancel: true });
     * @example：new Dialog().init({ lock: true, background: '#000', opacity: 0.75, title: '确认', content: '已经执行成功！', cancelVal: '关闭', cancel: true });
     * @example: <input type = "text" value = "0" name = "dValue" id = "dValue" />
     *           new Dialog().init({lock:true, background:'#000', opacity:0.75, width:'240px', title:'确认', content:'是否确定取消关注？', okVal:'确定', cancelVal:'取消', cancel:false, esc:false,
     *               close:function () {
     *                   if ($("#dValue").val() == "0") {
     *                       this.call();
     *                       return false;
     *                   }
     *               }, ok:function () {
     *                   $("#dValue").val("1");
     *               }
     *           });
     * @param strConfig
     * @returns {*}
     */
    Dialog.prototype.init = function(strConfig) {
        return $.dialog(strConfig);
    };

    /**
     * @description: @description:
     * @param dialogId
     */
    Dialog.prototype.dialogClose = function(dialogId) {
        $.dialog.list[dialogId].close();
    };

    /**
     * @description: Popup Confirm Dialog
     * @param {String} strTitle,
     * @param {String} strContent
     * @param {func} Function Callback
     * @Sample：dw.ui.iframe('dialog_login.php',{title: "登录",fixed: true,lock: true, background: '#000', opacity: 0.75, width: 505, height: 344,padding:0, resize:false,drag:false});
     */
    Dialog.prototype.iframe = function(strUrl, strConfig) {

        //dw.ui.iframe('dialog_login.php',{id: "loginWin",title: "登录",fixed: true,lock: true, background: '#000', opacity: 0.75, width: 505, height: 344,padding:0, resize:false,drag:false, cancel: true});
        return $.dialog.open(strUrl, strConfig);
    };

    Dialog.prototype.iframe.top = function() {
        return $.dialog.top;
    };

    /**
     *  Nested iframe within an iframe dialog
     * @param strUrl
     * @param strConfig
     * @param boolHasCache
     */
    Dialog.prototype.iframe.nestedIframe = function(strUrl, strConfig, boolHasCache) {
        $.dialog.load(strUrl, strConfig, boolHasCache);
    };

    /**
     *  Nested popup dialog within an iframe dialog
     * @param strConfig
     * @return {*}
     */
    Dialog.prototype.iframe.nestedDialog = function(strConfig) {
        var throughBox = $.dialog.through;
        return throughBox(strConfig);
    };

    Dialog.prototype.iframe.opener = function() {
        return $.dialog.opener;
    };

    Dialog.prototype.iframe.origin = function() {
        return $.open.origin;
    };

    /**
     * @description: Transfer data through iframe in dialog mode
     * @param strUrl
     * @param strConfig
     * @return {*}
     */
    Dialog.prototype.iframeData = function(strUrl, strConfig) {
        $.dialog.data('test', document.getElementById('demoInput04-3').value);
        return $.dialog.open(strUrl, null, false);
    };

    /**
     * @description: Close popup iframe window
     * @param dialogId
     */
    Dialog.prototype.iframeClose = function(dialogId) {
        var api = art.dialog.open.api;
        api && api.close();
        $.dialog.list[dialogId].close();
    };

    Dialog.prototype.tooltip = function() {

    };

    /**
     * 消息确认窗口
     * @param {String} content 需要显示的提示内容
     * @param {Function} yesFunc 确定按钮回调函数
     * @param {Function} noFunc 取消按钮回调函数
     * @return {Object} dialog 当前调用的jquery元素对象
     * @version 2013-09-22
     */
    Dialog.prototype.confirm = function(content, yesFunc, noFunc, okText, cancelText) {
        // return $.dialog.confirm(content, yesFunc, noFunc);
        return $.dialog({
            path: skinPath,
            icon: 'question',
            fixed: true,
            lock: true,
            // opacity: 0.1,
            content: content,
            okVal: okText || '确定',
            cancelVal: cancelText || '取消',
            ok: typeof yesFunc === 'function' ? yesFunc : true,
            cancel: typeof noFunc === 'function' ? noFunc : true
        });
    };

    /**
     * 消息提示窗口
     * @param {String} 需要显示的提示内容
     * @param {Function} 窗口关闭回调函数
     * @return {Object} 当前调用的jquery元素对象
     * @author luoweiping
     * @version 2013-09-24
     * @since 2013-06-26
     */
    Dialog.prototype.alert = function(content, callback) {
        // return $.dialog.alert(content, callback);
        return $.dialog({
            path: skinPath,
            icon: 'warning',
            fixed: true,
            lock: true,
            content: content,
            ok: true,
            close: callback
        });
    };

    /**
     * 短信发送弹窗
     * @param {Object} 弹窗配置参数对象
     * @return {Object} 当前调用的jquery元素对象
     * @author luoweiping
     * @version 2013-06-26
     * @since 2013-06-25
     */
    Dialog.prototype.smsWin = function(cfgObj) {
        var defaultCfg;

        defaultCfg = {
            title: '短信发送',
            padding: '3px 8px',
            lock: true
        };
        cfgObj = cfgObj || {};

        return $.dialog($.extend(defaultCfg, cfgObj));
    };

    /**
     * 短信模板弹窗
     * @param {Object} cfgObj 弹窗配置参数对象
     * @return {Object} 当前调用的jquery元素对象
     * @author luoweiping
     * @version 2013-06-26
     * @since 2013-06-25
     */
    Dialog.prototype.smsTplWin = function(cfgObj) {
        var defaultCfg;

        defaultCfg = {
            title: '短信模板',
            padding: '0px 3px 3px 0px',
            lock: true
        };
        cfgObj = cfgObj || {};

        return $.dialog($.extend(defaultCfg, cfgObj));
    };

    /*自动关闭的提示弹窗*/
    Dialog.prototype.tinyAlert = function(msg, senonds) {
        var timer;
        return $.dialog({
            path: skinPath,
            icon: 'warning',
            fixed: true,
            lock: true,
            ok: true,
            content: msg,
            close: function(){
                clearInterval(timer);
            },
            init: function () {
                var me = this;
                var i = senonds || 3;
                var fn = function () {
                    me.title(i + '秒后自动关闭');
                    if(i === 0) {
                        me.close();
                    }
                    i --;
                };
                timer = setInterval(fn, 1000);
                fn();
            }
        });
    };

    module.exports = Dialog;
});