import sidereal
# -*- coding: utf-8 -*-

s1 = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>GRB Alert</title>

<script type="text/javascript">
<!--
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
<body onload="updateClock(); setInterval('updateClock()', 1000 );diffClock(); setInterval('diffClock()', 1000 )">
<table border="0" cellpadding="5" cellspacing="5" width="100%">
<tr>
  <th colspan="2">
    <H1>Swift GRB Alert</H1>
  </th>
</tr>
<tr>
  <td width="50%">
    <IMG SRC="http://casjobs.sdss.org/ImgCutoutDR7/getjpeg.aspx?ra=
"""
s3 = """&scale=0.6&width=700&height=550">
  </td>
  <td>
    <table border="0" cellpadding="1" cellspacing="1" width="100%">
      <tr>
	<td width="25%">
	  published
	</td>
	<td>
"""
s4 = """</td>
      </tr>
      <tr>
	<td width="25%">
	  updated
	</td>
	<td>
"""
s5 = """</td>
      </tr>
      <tr>
	<td width="25%">
	  RA
	</td>
	<td>
"""
s6 = """&#176;
	</td>
      </tr>
      <tr>
	<td width="25%">
	  Dec
	</td>
	<td>
"""
s7 = """&#176;
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
s8 = """</td>
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
s9 = """</td>
      </tr>
      <tr>
	<td width="25%">
	  Dec
	</td>
	<td>
"""
s10 = """</td>
      </tr>
      <tr>
	<td width="25%">
	  h
	</td>
	<td>
"""
s11 = """&#176;
	</td>
      </tr>
      <tr>
	<td width="25%">
	  sec(z)
	</td>
	<td>
"""
s12 = """
</td>
      </tr>
    </table>
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
<H2>DSS image (15'x15')</H2>
"""
s13 = """
<IMG SRC="http://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r=
"""
s14 = """&e=J2000&h=15.0&w=15.0&f=gif&c=none&fov=NONE&v3=">
"""
s15 = """
</body>
</html>
"""
def GenHTML(datestr,RA,DEC,nicedate,h,secz):
    dms = sidereal.MixedUnits( (60,60) )
    RAlist = dms.singleToMix( RA/15.0 )
    DEClist = dms.singleToMix( DEC )
    RAnice = str(RAlist[0])+"h "+str(RAlist[1])+"m "+str(RAlist[2])+"s"
    DECnice = str(DEClist[0])+"° "+str(DEClist[1])+"' "+str(DEClist[2])+'"'
    s = s1 + datestr + s2 + str(RA) + "&dec=" + str(DEC) + s3
    s = s + datestr + s4 + datestr + s5 #FIXME second is updated
    s = s + str(RA) + s6 + str(DEC) + s7 + nicedate
    s = s + s8 + RAnice + s9 + DECnice + s10
    s = s + str(h) + s11 + str(secz) + s12
    s = s + s13 + str(RA) + "&d=" + str(DEC) + s14 + s15
    fop = open("FindingChart.html","w")
    fop.write(s)
    fop.close()