
  $(function() {



   /////////////////////////////////////////////////////////////////////
   /////////////////////////////////////////////////////////////////////

   //////////////////////// GET NAME TIMELINE .///////////////////////
   function info() {
     $.ajax({
         url: "/info",
         dataType: "json"
     })
     .done(function(r) {
       console.log(r)
       $("#timeline_group").text(r.timeline.group);
       $("#timeline_version").text(r.timeline.version+" UTC+0");

       $("#device_name").text(r.device.name).css("font-weight","Bold");
       $("#device_info").text(r.device.settings.infos);
       $("#device_voltage").text(r.device.voltage+" V");
       $("#device_bat").text(r.device.settings.tension);

       $("#system_branch").text(r.system.branch);
       var commit = '';
       $.each(r.system.commit, function(index, com) {
         if (index > 1) commit += "<br />";
         else commit += " - ";
         commit += com;
       });
       $("#system_commit").html(commit);

       $("#scenes").empty();
       $.each(r.timeline.scenes, function(index, scene) {
         var line = $('<div class="line">');
         if (index == r.timeline.activescene) line.addClass('lineactive');
         line.append(scene);
         line.data('id', index);
         line.on("click", function(e) {
           var idScene = $(this).data('id');
           console.log('clicked '+idScene);
           $.ajax({
               url: "/changeScene",
               type: "POST",
               data: { scene: idScene }
           })
           .done(function(r) {
             info();
           });
         });
         $("#scenes").append(line);
       });
     });
   }
   setInterval(info,2000);
   info();

});
