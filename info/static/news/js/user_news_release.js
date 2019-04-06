function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    $(".release_form").submit(function (e) {
        e.preventDefault();

        /*
        $.ajax({}); get post
        一般用于传输纯文本的字符串
        表单中的带有name的input标签的值，都需要程序员自己写代码读取

        $(this).ajaxSubmit({});
        一般用于传入不是纯文本的数据的：比如一个表单中input type=text   / type=file
        注意：会自动的以表单的行为取读取表单中带有name的input标签的值，从而程序员不需要手动的读取
        不用传递data
        */

        // TODO 发布完毕之后需要选中我的发布新闻
        $(this).ajaxSubmit({

            // 读取富文本编辑器里面的文本信息
            beforeSubmit: function (request) {
                // 在提交之前，对参数进行处理
                for(var i=0; i<request.length; i++) {
                    var item = request[i];
                    if (item["name"] == "content") {
                        item["value"] = tinyMCE.activeEditor.getContent()
                    }
                }
            },
            url: "/user/news_release",
            type: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    // 选中索引为6的左边单菜单
                    window.parent.fnChangeMenu(6)
                    // 滚动到顶部
                    window.parent.scrollTo(0, 0)
                }else {
                    alert(resp.errmsg)
                }
            }
        });
    });
});