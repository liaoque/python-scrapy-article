export default ({ service, request, serviceForMock, requestForMock, mock, faker, tools }) => ({
  /**
   * @description 登录
   * @param {Object} data 登录携带的信息
   */
  YUAN_YIN (data = {}) {
    // /api/wb/?current_time=20230913
    return request({
      url: 'wb/?current_time=20230913',
      method: 'get',
      data: {
        current_time: '20230913'
      }
    })
  }
})
