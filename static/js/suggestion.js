$(".suggest").click(function () {
    alert(123);
    $.ajax({

        url:'/suggest/',
        type:'post',
        data:{

            csrfmiddlewaretoken:$("[name='csrfmiddlewaretoken']").val()
        },
        success:function (data) {
            console.log(data)
        }
    })
});