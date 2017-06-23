
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

       $("#signals").empty();
       $.each(r.timeline.signals, function(index, signal) {
         var line = $('<div class="line">');
         //if (index == r.timeline.activescene) line.addClass('lineactive');
           if (signal.lastIndexOf("split_", 0) === 0){
               return; // skip split_XXXX signals
           }
           var signalName = signal;
           if(signalName == "CARTE_PUSH_1"){
               signalName = "PUSH COURT";
           }else if(signalName == "CARTE_PUSH_11"){
               signalName = "PUSH LONG";
           }else if(signalName == "TELECO_PUSH_OK"){
               signalName = "TELECO OK ";
           }else if(signalName == "TELECO_PUSH_A"){
               signalName = "TELECO A";
           }else if(signalName == "TELECO_PUSH_B"){
               signalName = "TELECO B";
           }
         line.append(signalName);
         line.data('id', signal);
         line.on("click", function(e) {
           var idSignal = $(this).data('id');
           console.log('clicked '+idSignal);
             $(this).addClass('lineactive');
           $.ajax({
               url: "/sendSignal",
               type: "POST",
               data: { signal: idSignal }
           })
           .done(function(r) {
             info();
           });
         });
         $("#signals").append(line);
       });

         $("#state").empty();
       $.each(r.timeline.signals, function(index, content) {
           if (index == "titreur") {
               var state = $('<div class="line">');
               state.append("<strong>TITREUR</strong>");
               state.addClass('lineactive');
               state.data('id', index);
               $("#state").append(state);
               $.each(content, function (elem, value) {
                   var line = $('<div class="line">');
                 if (elem == "line1" || elem == "line2"){
                     line.append(value)
                 }
                   $("#state").append(line);
               });
           }
       });

     });
   }
   setInterval(info,2000);
   info();

});
