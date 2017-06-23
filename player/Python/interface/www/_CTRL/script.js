
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
       $.each(r.device.state, function(index, content) {
           var state = $('<div class="line">');
           if (index == "titreur") {
               state.append("<strong>TITREUR</strong>");
               state.addClass('lineactive');
               state.data('id', index);
               $("#state").append(state);
               var line1 = $('<div class="line">');
               var line2 = $('<div class="line">');
               $("#state").append(line1);
               $("#state").append(line2);
               $.each(content, function (elem, value) {
                 if (elem == "line1"){
                     line1.append(value);
                 }else if(elem == "line2"){
                     line2.append(value);
                 }
               });
           }else if(index == "light"){
               state.append("<strong>LIGHT</strong>");
               state.addClass('lineactive');
               state.data('id', index);
               $("#state").append(state);
               $.each(content, function (elem, value) {
                   var line = $('<div class="line">');
                 if (elem == "rgb") {
                     //console.log(value);
                     //var color = JSON.parse(value);
                     line.append("R:"+value.R+" G:"+value[1]+"B:"+value[2]+" " +
                         "<div style='height:10px; widht:10px;" +
                         " background-color: rgb("+value[0]+","+value[1]+","+value[2]+");'></div>");
                     $("#state").append(line);
                 }
               });
           }
       });

     });
   }
   setInterval(info,2000);
   info();

});
