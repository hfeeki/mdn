<?php 
function head(
  $title='Mozilla Developer Network', 
  $pageid='', 
  $bodyclass='',
  $headerclass=''
) { 
?>
<!DOCTYPE html>
<html lang="en-US" dir="ltr" id="developer-mozilla-org">
<head>
  <title><?php echo $title ?></title>
	
	<meta charset="utf-8">
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="MSSmartTagsPreventParsing" content="true">
  <meta name="ROBOTS" content="ALL">
  <meta name="Copyright" content="Copyright (c) 2005-<?php echo date(Y); ?> Mozilla.">
  <meta name="Rating" content="General">
  
  <link rel="home" href="/">
  <link rel="copyright" href="#legal-copyright">
  
  <!--[if !IE 6]><!--><link rel="stylesheet" type="text/css" media="screen,projection" href="./css/screen.css"><!--<![endif]-->
  <!--[if IE]><link rel="stylesheet" type="text/css" media="all" href="./css/ie.css"><![endif]-->
  <!--[if lte IE 7]><link rel="stylesheet" type="text/css" media="all" href="./css/ie7.css"><![endif]-->
  <!--[if lte IE 6]><link rel="stylesheet" type="text/css" media="all" href="./css/ie6.css"><![endif]-->
  <link rel="stylesheet" type="text/css" media="print" href="./css/print.css">
  
  <script type="text/javascript" src="./js/jquery-1.4.2.min.js"></script>

  <!--[if IE]>
  <meta http-equiv="imagetoolbar" content="no">
  <meta http-equiv="X-UA-Compatible" content="IE=Edge">
  <script src="./js/html5.js"></script>
  <![endif]-->
  
</head>
<body id="<?php echo $pageid; ?>" class="<?php echo $bodyclass; ?>" role="document">
<!--[if lte IE 8]>
<noscript><div class="global-notice">
<p><strong>Warning:</strong> The Mozilla Developer Network website employs emerging web standards that may not be fully supported in some versions of MicroSoft Internet Explorer. You can improve your experience of this website by enabling JavaScript.</p>
</div></noscript>
<![endif]-->
<header id="masthead" class="<?php echo $headerclass; ?>">
  <div class="wrap">
    <div id="branding">
    <?php if ($headerclass == 'major') : /* big logo */ ?>
      <h1 id="logo"><a href="home.php"><img src="./img/mdn-logo.png" alt="" width="128" height="146"> Mozilla Developer Network</a></h1>
    <?php elseif ($headerclass == 'compact') : /* compact logo */ ?>
      <h1 id="logo"><a href="/"><img src="./img/mdn-logo-compact.png" alt="Mozilla Developer Network" title="Mozilla Developer Network" width="135" height="40"></a></h1>
    <?php else : ?>
      <h1 id="logo"><a href="home.php"><img src="./img/mdn-logo-sm.png" alt="" width="62" height="71"> Mozilla Developer Network</a></h1>    
    <?php endif; ?>
    <?php if ($headerclass != 'compact') : /* No tagline in the compact header */ ?>
      <p id="tagline">A comprehensive, usable &amp; accurate resource for everyone developing for the Open Web.</p>
    <?php endif; ?>
    </div>
    
    <div id="utility">
      <p class="user-state"><a href="#">Log in</a> | <a href="#">Become an MDN member</a></p>
      <form id="site-search" method="get" action="#">
        <p><input type="text" role="search" placeholder="Search MDN" id="q" name="q" /> <button type="submit">Search</button></p>
<!--         <div id="site-search-gg"><div class="gsc-branding"><table class="gsc-branding" cellpadding="0" cellspacing="0"><tbody><tr><td class="gsc-branding-text"><div class="gsc-branding-text">powered by</div></td><td class="gsc-branding-img-noclear"><img class="gsc-branding-img-noclear" src="http://www.google.com/uds/css/small-logo.png"></td></tr></tbody></table></div></div> -->
      </form>
    </div>
  
  <?php if ($headerclass == 'compact') : /* compact nav */ ?>
    <nav id="nav">
    <?php if (strpos($bodyclass,'demos')) : ?>
      <h2 class="current"><a href="demos-landing.php">Demos</a></h2>
    <?php elseif (strpos($bodyclass,'learning')) : ?>
      <h2 class="current"><a href="learn-landing.php">Learning</a></h2>
    <?php endif; ?>
      <div class="menu"><a href="#nav-main" class="toggle" title="Explore other parts of MDN">Explore MDN</a>
        <ul id="nav-main" class="sub-menu" role="navigation">
          <li id="nav-main-web"><a href="section-web.php" class="web">Web</a></li>
          <li id="nav-main-mobile"><a href="section-mobile.php" class="mobile">Mobile</a></li>
          <li id="nav-main-addons"><a href="section-addons.php" class="addons">Add-ons</a></li>
          <li id="nav-main-mozilla"><a href="section-apps.php" class="mozilla">Mozilla</a></li>
          <li id="nav-extra-docs"><a href="docs-landing.php">Docs</a></li>
        <?php if (strpos($bodyclass,'demos')) : ?>
          <li id="nav-extra-learning"><a href="learn-landing.php">Learning</a></li>
        <?php elseif (strpos($bodyclass,'learning')) : ?>
          <li id="nav-extra-learning"><a href="demos-landing.php">Demos</a></li>
        <?php endif; ?>
          <li id="nav-extra-forums"><a href="./forum">Forums</a></li>      
        </ul>
      </div>
    </nav>
  
    <script type="text/javascript">
      // <![CDATA[
      $(document).ready(function() {
        $("#nav").addClass("js");
      	
        $("#nav .toggle").click(function() {
          $("#nav-main").slideToggle(100);
          return false;
        });
        
        $("#nav-main").hover(
          function() {
            $(this).show();
            $("#nav .menu").addClass('hover');
          },
          function() {
            $(this).slideUp('fast');
            $("#nav .menu").removeClass('hover');
            $("#nav .toggle").blur();
          }
        );
  
        $(document).bind('click', function(e) {
          var $clicked = $(e.target);
          if (! $clicked.parents().hasClass("menu"))
            $("#nav-main").hide();
        });
        
        $("a, input, textarea, button").bind('focus', function(e) {
          var $focused = $(e.target);
          if (! $focused.parents().hasClass("menu"))
            $("#nav-main").hide();
        });
  
      });
      // ]]>
    </script>

  <?php else : /* regular nav */ ?>
  
    <nav id="nav">
      <ul id="nav-main" role="navigation">
        <li id="nav-main-web"><a href="section-web.php" class="web">Web</a></li>
        <li id="nav-main-mobile"><a href="section-mobile.php" class="mobile">Mobile</a></li>
        <li id="nav-main-addons"><a href="section-addons.php" class="addons">Add-ons</a></li>
        <li id="nav-main-mozilla"><a href="section-apps.php" class="mozilla">Mozilla</a></li>
      </ul>
  
      <ul id="nav-extra" role="navigation">
        <li id="nav-extra-docs"><a href="docs-landing.php">Docs</a></li>
        <li id="nav-extra-demos"><a href="demos-landing.php">Demos</a></li>
        <li id="nav-extra-learning"><a href="learn-landing.php">Learning</a></li>
        <li id="nav-extra-community"><a href="./forum/">Forums</a></li>
      </ul>
    </nav>
  
  <?php endif; ?>
    
  </div>
</header>
<?php } // end head ?>


<?php function foot() { ?>
<section id="footbar">
<div class="wrap">
  <p>What do you think of the new MDN? Please <a href="#">share your feedback</a> with us.</p>
</div>
</section>
<footer id="site-info" role="contentinfo">
<div class="wrap">
    <div id="legal">
      <img src="./img/mdn-logo-tiny.png" alt="" width="42" height="48">
      <p id="copyright">&copy; <?php echo date('Y'); ?> Mozilla Developer Network</p>
      <p>Content is available under <a href="#">these licenses</a> &bull; <a href="#">About MDN</a> &bull; <a href="#">Help</a></p>
    </div>
    <p class="user-state"><a href="#">Log in</a> | <a href="#">Become an MDN member</a></p>

    <form class="languages go" method="get" action="">
      <label for="language">Other languages:</label>
      <select id="language" name="lang" dir="ltr">
          <option value="en-US" selected="selected">English</option>
          <option value="de">German</option>
          <option value="es">Spanish</option>
          <option value="kl">Klingon</option>
          <option value="el">Elvish</option>
          <option value="etc">And so on&hellip;</option>
      </select>
      <noscript><button type="submit">Go</button></noscript>
    </form>
 
</div>
</footer>
<script type="text/javascript">
$(document).ready(function() {
  // Set up input placeholders.
  $('input[placeholder]').placeholder();
}); 

/* Fake the placeholder attribute since Firefox doesn't support it. */
jQuery.fn.placeholder = function(new_value) {
  if (new_value) {
    this.attr('placeholder', new_value);
  }

  /* Bail early if we have built-in placeholder support. */
  if ('placeholder' in document.createElement('input')) {
    return this;
  }

  if (new_value && this.hasClass('placeholder')) {
    this.val('').blur();
  }

  return this.focus(function() {
    var $this = $(this),
    text = $this.attr('placeholder');

    if ($this.val() == text) {
      $this.val('').removeClass('placeholder');
    }
  }).blur(function() {
    var $this = $(this),
    text = $this.attr('placeholder');

    if ($this.val() == '') {
      $this.val(text).addClass('placeholder');
    }
  }).each(function(){
    /* Remove the placeholder text before submitting the form. */
    var self = $(this);
    self.closest('form').submit(function() {
      if (self.hasClass('placeholder')) {
        self.val('');
      }
    });
  }).blur();
};

</script>
</body>
</html>
<?php } // end foot ?>
