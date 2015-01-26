seajs.config({
    // 映射,添加版本号
    map: [[/^(.*\.(?:css|js))$/i, '$1?v=1.0.0']],
    // 别名配置
    alias: {
        'jquery': 'lib/jquery/src/jquery-1.10.1.min',
        'dialog': 'lib/dialog/main',//定义artDialog的接口
        'highCharts': 'lib/highcharts/main',//图表插件
        'util':'lib/util/main'//工具
    },
    // 插件
    // plugins: ['shim', 'text', 'debug', 'nocache'], // for development
    // 预加载项
    preload: ["jquery"],
    // 文件编码
    charset: 'utf-8'
});
