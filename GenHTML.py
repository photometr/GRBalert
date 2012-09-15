# -*- coding: utf-8 -*-
import sidereal
import math

s1 = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>GRB Alert</title>

<!-- image handling -->
  <!-- SDSS image manipulation -->
  <script type="text/javascript" src="./pixastic.core.js"></script>
  <script type="text/javascript" src="./rotate.js"></script>
  <script type="text/javascript" src="./fliph.js"></script>
  <script type="text/javascript">
  function sdss_hor_flip() {
	  Pixastic.process(document.getElementById("sdss"), "fliph")
  }
  </script>
  <script type="text/javascript">
  function sdss_rotate180() {
	  Pixastic.process(document.getElementById("sdss"), "rotate", {
		  angle : 180
	  });
  }
  </script>
  <script type="text/javascript">
  function sdss_rotate25() {
	  Pixastic.process(document.getElementById("sdss"), "rotate", {
		  angle : -25
	  });
  }
  </script>
  <script type="text/javascript">
  function sdss_rotate155() {
	  Pixastic.process(document.getElementById("sdss"), "rotate", {
		  angle : -155
	  });
  }
  </script>

<!-- DSS image manipulation -->
  <script type="text/javascript" src="./pixastic.core.js"></script>
  <script type="text/javascript" src="./rotate.js"></script>
  <script type="text/javascript" src="./fliph.js"></script>
  <script type="text/javascript">
  function hor_flip() {
	  Pixastic.process(document.getElementById("dss"), "fliph")
  }
  </script>
  <script type="text/javascript">
  function rotate180() {
	  Pixastic.process(document.getElementById("dss"), "rotate", {
		  angle : 180
	  });
  }
  </script>
  <script type="text/javascript">
  function rotate25() {
	  Pixastic.process(document.getElementById("dss"), "rotate", {
		  angle : -25
	  });
  }
  </script>
  <script type="text/javascript">
  function rotate155() {
	  Pixastic.process(document.getElementById("dss"), "rotate", {
		  angle : -155
	  });
  }
  </script>

<!-- time operations-->
<script type="text/javascript">
function updateClock ( )
{
  var currentTime = new Date ( );

  var currentHours = currentTime.getUTCHours ( );
  var currentMinutes = currentTime.getUTCMinutes ( );
  var currentSeconds = currentTime.getUTCSeconds ( );

  // Pad the minutes and seconds with leading zeros, if required
  currentMinutes = ( currentMinutes < 10 ? "0" : "" ) + currentMinutes;
  currentSeconds = ( currentSeconds < 10 ? "0" : "" ) + currentSeconds;

  // Compose the string for display
  var currentTimeString = currentHours + ":" + currentMinutes + ":" + currentSeconds;

  // Update the time display
  document.getElementById("clock").firstChild.nodeValue = currentTimeString;
}
function diffClock ( )
{
  var event = Date.parse("'''
s2 = """");
  var now = new Date ( );
  var curtime = now.valueOf();
  var delta = (curtime - event)/1000;
  var deltaH = Math.floor(delta/3600); //Since it's always positive
  var minmod = delta % 3600
  var deltaM = Math.floor(minmod/60);
  var deltaS = Math.floor(minmod % 60);
  
  deltaH = ( deltaH < 10 ? "0" : "" ) + deltaH;
  deltaM = ( deltaM < 10 ? "0" : "" ) + deltaM;
  deltaS = ( deltaS < 10 ? "0" : "" ) + deltaS;

  var currentTimeString = deltaH + ":" + deltaM + ":" + deltaS;

  // Update the time display
  document.getElementById("timediff").firstChild.nodeValue = currentTimeString;
}
// -->
</script>

</head>
<body onload="updateClock(); setInterval('updateClock()', 1000 );diffClock(); setInterval('diffClock()', 1000 );sdss_hor_flip();hor_flip()">
<table border="0" cellpadding="5" cellspacing="5" width="100%">
<tr>
  <th colspan="2">
    <H1>Swift GRB Alert <font color="red">"""
s3 = """</font></H1>
     <a href="WhatShouldIDo.html">Как навестись и что снимать?</a>
  </th>
</tr>
<tr>
  <td width="50%">
  <H2>SDSS image (7'x5.5')</H2>
  комментарии к кнопкам <a href="#buttoncomm">ниже</a></br>
<input type="button" onclick="sdss_rotate180();" value="W"/>
<input type="button" onclick="sdss_rotate25();" value="+25 E"/>
<input type="button" onclick="sdss_rotate155();" value="+25 W"/>
<input type="button" onclick="window.location.reload()" value="reset"/></br>
    <IMG SRC="http://casjobs.sdss.org/ImgCutoutDR7/getjpeg.aspx?ra=
"""
s4 = """&scale=0.6&width=700&height=550" id="sdss" alt="sdss finding chart">
  </td>
  <td>
    <table border="0" cellpadding="1" cellspacing="1" width="100%">
      <tr>
	<td width="25%">
	  published
	</td>
	<td>
"""
s5 = """</td>
      </tr>
      <tr>
	<td width="25%">
	  updated
	</td>
	<td>
"""
s6 = """</td>
      </tr>
      <tr>
	<td width="25%">
	  RA
	</td>
	<td>
"""
s7 = """&#176;
	</td>
      </tr>
      <tr>
	<td width="25%">
	  Dec
	</td>
	<td>
"""
s8 = """&#176;
	</td>
      </tr>
    </table>
    <br>
    <br>
    <table border="0" cellpadding="1" cellspacing="1" width="100%">
      <tr>
	<td width="25%">
	  Registered
	</td>
	<td>
"""
s9 = """</td>
      </tr>
      <tr>
	<td width="25%">
	  UTC
	</td>
	<td>
	  <span id="clock">&nbsp;</span> 
	</td>
      </tr>
      <tr>
	<td width="25%">
	  Time Delta
	</td>
	<td>
	  <span id="timediff" style="color:red">&nbsp;</span> 
	</td>
      </tr>
      <tr>
	<td width="25%">
	  RA
	</td>
	<td>
"""
s10 = """</td>
      </tr>
      <tr>
	<td width="25%">
	  Dec
	</td>
	<td>
"""
s11 = """</td>
      </tr>
      <tr>
	<td width="25%">
	  h
	</td>
	<td>
"""
s12 = """&#176;
	</td>
      </tr>
      <tr>
	<td width="25%">
	  sec(z)
	</td>
	<td>
"""
s13 = """
</td>
      </tr>
    </table>
    <br>
    <a href="http://gcn.gsfc.nasa.gov/gcn3_archive.html">GCN Circulars</a>
    <br>
    <a href="http://gcn.gsfc.nasa.gov/gcn_describe.html">The GCN/TAN System</a>
    <br>
    <a href="http://cas.sdss.org/dr7/en/tools/chart/chart.asp">SDSS Finding Chart</a>
    <br>
    <a href="http://archive.stsci.edu/cgi-bin/dss_form">DSS Finding Chart</a>
    <br>
    <a href="http://www.skyalert.org/">SkyAlert</a>
  </td>
</tr>
</table>
<br>
<H2>DSS image (15'x15')</H2> комментарии к кнопкам <a href="#buttoncomm">ниже</a></br>
<input type="button" onclick="rotate180();" value="W"/>
<input type="button" onclick="rotate25();" value="+25 E"/>
<input type="button" onclick="rotate155();" value="+25 W"/>
<input type="button" onclick="window.location.reload()" value="reset"/></br>
"""
s14 = """
<IMG SRC="http://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r=
"""
s15 = """&e=J2000&h=15.0&w=15.0&f=gif&c=none&fov=NONE&v3=" id="dss" alt="dss finding chart"></br>
"""
s16 = """
<a name="buttoncomm">Кнопки имеют следующее значение</a></br>
Загружаемое изображение это отражённая относительно вертикальной оси картинка с SDSS/DSS, т.е. так видно в CCDops при нулевом повороте камеры, когда телескоп с Востока.</br>
Кнопка <input type="button" value="W"/> поворачивает его на 180&#176;, т.е. так как будет видно в CCDops при нулевом повороте камеры, когда телескоп с Запада.</br>
Кнопка <input type="button" value="+25 E"/> так будет в CCDops при повороте камеры +25&#176; если телескоп с Востока.</br>
Кнопка <input type="button" value="+25 W"/> так будет в CCDops при повороте камеры +25&#176; если телескоп с Запада.</br>
Кнопка <input type="button" value="reset"/> сбрасывает в начальное положение.
</body>
</html>
"""
def GenHTML(datestr,RA,DEC,nicedate,h,secz,telescope,pos_err):
    if pos_err is None:
      RADEC_err_min = "<font color='red'>   ± ?</font>"
      Err = " ± ?"
    else:
      RADEC_err_min = "<font color='red'>   ± "+str(round(pos_err*60,2))+"'</font>"
      Err = " ± "+ str(pos_err)
    dms = sidereal.MixedUnits( (60,60) )
    RAlist = dms.singleToMix( RA/15.0 )
    DEClist = dms.singleToMix( abs(DEC) )
    RAnice = str(RAlist[0])+"h "+str(RAlist[1])+"m "+str(int(round(RAlist[2])))+"s"+ RADEC_err_min
    DECnice = str(math.copysign(DEClist[0],DEC))+"° "+str(DEClist[1])+"' "+str(int(round(DEClist[2])))+'"'+ RADEC_err_min
    s = s1 + datestr + s2+ telescope + s3 + str(RA) + "&dec=" + str(DEC) + s4
    s = s + datestr + s5 + datestr + s6 #FIXME second is updated
    s = s + str(RA) + Err + s7 + str(DEC) + Err + s8 + nicedate
    s = s + s9 + RAnice + s10 + DECnice + s11
    s = s + str(h) + s12 + str(secz) + s13
    s = s + s14 + str(RA) + "&d=" + str(DEC) + s15 + s16
    fop = open("FindingChart.html","w")
    fop.write(s)
    fop.close()