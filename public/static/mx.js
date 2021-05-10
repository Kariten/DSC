function getUserInfo(token,callback) {
    fetch("../api/getuserinfo", {
        method: 'POST',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
                token : token
            }
        )
    }).then(res => {
            return res.json()
        }
    ).then(res => {
        console.log(res.msg)
        if (res.code === '0') {
            return res.data
        }
        layer.msg("用户信息获取失败")
    }).then(callback)
}