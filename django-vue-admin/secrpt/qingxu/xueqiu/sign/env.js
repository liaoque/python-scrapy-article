log_ = console.log;
setTimeout = function () {}
setInterval = function () {}
console.log = function () {
}
window = global;
window.hasOwnProperty = function (res) {
    return res == 'origin'
}
window.XMLHttpRequest = {
    prototype :{}
}
window.self = window
window.screen = {
    availHeight: 792,
    availLeft: 0,
    availTop: 25,
    availWidth: 1440,
    colorDepth: 24,
    height: 900,
    isExtended: false,
    onchange: null,
    pixelDepth: 24,
    width: 1440
}
window.innerWidth = 156
window.refresh = 156


delete global;
global = {}
// delete Buffer;
HTMLCollection = {
    firstChild: function () {
        return null
    },
    length: 0
}

location = {
    "ancestorOrigins": {},
     "href": "https://xueqiu.com/",
    "origin": "https://xueqiu.com/",
    "protocol": "https:",
    "host": "xueqiu.com",
    "hostname": "xueqiu.com",
    "port": "",
    "pathname": "/",
    "search": "",
    "hash": ""
}
document = {

    head: {
        insertBefore: function (r, r2) {
        },
        firstChild: function () {
            return null
        },
    },
    firstChild: function () {
        return null
    },
    location: location,
    createElement: function (res) {
        if (res === 'div') {
            return {firstChild: location}
        }
        // log_(res, "createElement")

        return {
            style: {
                zoom: ""
            },
            hasOwnProperty: function () {
            },
            remove:function () {}
        }
    },
    documentElement: {
        getAttribute: function () {
            return ''
        },

    },
    getElementsByTagName: function (tagName) {
        return HTMLCollection
    }

};
navigator = {
    appCodeName: "Mozilla",
    appName: "Netscape",
    appVersion: "5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    webdriver: false,
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    plugins: {
        refresh: function () {
            
        }
    }
};

function setProxyArr(proxyObjArr) {
    for (let i = 0; i < proxyObjArr.length; i++) {
        const handler = `{
      get: function(target, property, receiver) {
        log_("方法:", "get  ", "对象:", "${proxyObjArr[i]}", "  属性:", property, "  属性类型：", typeof property, ", 属性值：", target[property], ", 属性值类型：", typeof target[property]);
        return target[property];
      },
      set: function(target, property, value, receiver) {
        log_("方法:", "set  ", "对象:", "${proxyObjArr[i]}", "  属性:", property, "  属性类型：", typeof property, ", 属性值：", value, ", 属性值类型：", typeof target[property]);
        return Reflect.set(...arguments);
      }
    }`;
        eval(`try {
            ${proxyObjArr[i]};
            ${proxyObjArr[i]} = new Proxy(${proxyObjArr[i]}, ${handler});
        } catch (e) {
            ${proxyObjArr[i]} = {};
            ${proxyObjArr[i]} = new Proxy(${proxyObjArr[i]}, ${handler});
        }`);
    }
}

setProxyArr(['window', 'document', 'element', 'location', 'navigator', 'localStorage', 'cookie']);