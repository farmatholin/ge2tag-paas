"use strict";

$(function () {
    console.log('common init');

    $('.gt-start').click(function (e) {

        var $self = $(this);
        var $parent = $self.parent();
        var container = $self.data('name');

        console.log('start');
        send('start', container, function () {
             $('#container-' + container).find('.container-status').html('online');
            $parent.find('.gt-stop').show();
            $self.hide();
        });
    });

    $('.gt-stop').click(function (e) {
        var $self = $(this);
        var container = $self.data('name');
        var $parent = $self.parent();

        console.log('stop');
        send('stop', container, function () {
             $('#container-' + container).find('.container-status').html('online');
            $parent.find('.gt-start').show();
            $self.hide();
        });
        return false
    });

    $('.gt-remove').click(function (e) {
        var $self = $(this);
        var container = $self.data('name');
        console.log('remove');
        send('remove', container, function () {
             $('#container-' + container).remove();
        });
    });

    var send = function (cmd, container, callback) {
        $.ajax({
            type: "POST",
            url: "/user/container/cmd/" + container + '/' + cmd,
            success: function (data) {
                if(data.code == 200){
                    callback()
                }
            },
            error: function () {
                return false
            }
        });
    }
});