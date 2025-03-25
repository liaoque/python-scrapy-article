require('./env.js')
require('./sign2.js')

bV = "https%3A%2F%2Fxueqiu.com%2Flivestream%2Froom%2Fanchor%2Fquery.json%3F_%3D1742668408297"

d = {
    protocol: 'https:',
    host: 'xueqiu.com',
    hostname: 'xueqiu.com',
    port: '',
    pathname: "/statuses/hot/listV3.json",
    search: "?source=hot&page=1&_=1742835192790",
    hash: '',
    V: '"https://xueqiu.com/statuses/hot/listV3.json?source=hot&page=1&_=1742835192790"'
}
res = RL['D'](d, null, "GET")
log_(res)

// res = sign(b6, 6, function(bx) {
//     return b8['Ktbqh']['charAt'](bx);
// });


//
//aa = window.RL['D'](
//{"protocol":"https:","host":"xueqiu.com","hostname":"xueqiu.com","port":"","pathname":"/promotion/display.json","search":"?platform_id=0x05&page_id=0x05&pos_id=right_top&_=1742651206910","hash":"","V":"https://xueqiu.com/promotion/display.json?platform_id=0x05&page_id=0x05&pos_id=right_top&_=1742651206910"}
//,null, 'GET')
//log_(aa)