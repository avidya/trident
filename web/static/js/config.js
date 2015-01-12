seajs.config({
    // 映射,添加版本号
    map: [[/^(.*\.(?:css|js))$/i, '$1?v=1.0.0']],
    // 别名配置
    alias: {
        'jquery': 'jquery-1.10.1.min',
    },
    // 插件
    // plugins: ['shim', 'text', 'debug', 'nocache'], // for development
    // 预加载项
    preload: ["jquery"],
    // 文件编码
    charset: 'utf-8'
});
