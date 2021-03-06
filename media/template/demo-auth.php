<?php include "./inc/template.php"; 
head(
  $title = 'Submit a New Demo | Mozilla Developer Network',
  $pageid = '', 
  $bodyclass = 'section-demos',
  $headerclass = 'compact'
); ?>
<section id="nav-toolbar">
<div class="wrap">
  <nav class="crumbs">
    <ol role="navigation">
      <li><a href="home.php">MDN</a></li>
      <li><a href="demos-landing.php">Demo Studio</a></li>
      <li><a href="demo-auth.php">Submit a New Demo</a></li>
    </ol>
  </nav>
</div>
</section>

<section id="content">
<div class="wrap">

  <section id="content-main" role="main">
    
    <h1 class="page-title">Submit a New Demo</h1>
    <p>Whether you are creating an amazing new way to experience the Web or just experimenting with the latest technologies, we invite you to submit your own demos to share with (or show off to) other web developers.</p>

    <div class="modules">
      <div id="before-begin" class="module notes">
        <h3 class="mod-title">Before You Begin</h3>
        <ul>
          <li>You must be prepared to <strong>provide the source code</strong> for your demo. Demos are hosted on the Demo Studio’s servers.</li>
          <li>Your demo’s source code must be available under an <strong>open license</strong>, such as MPL, GPL, or BSD.</li>
          <li>Your demo should showcase <strong>open web technologies</strong>, such as HTML5 and CSS3.</li>
          <li>Your demo should support a wide range of <strong>modern web browsers</strong>, like Firefox, Chrome, Safari, and Opera.</li>
        </ul>
      </div>
  
      <div id="prepare-demo" class="module notes">
        <h3 class="mod-title">Preparing Your Demo</h3>
        <ul>
          <li>Your demo’s source code should be packaged inside a <strong>ZIP file</strong>.</li>
          <li>The main page of your demo should be a file named <strong><code>index.html</code></strong> in the root of the ZIP.</li>
          <li>Your demo should be build on <strong>client-side technology</strong> (HTML, CSS, JavaScript). Server-side languages like PHP and Ruby are not supported.</li>
          <li>If your demo requires external resources, it should use <strong>AJAX</strong> to access them.</li>
        </ul>
      </div>
    </div>

    <p>To submit your demo, you need an <strong><a href="/register">MDN account</a></strong>.</p>
    
    <p class="choices"><a href="#" class="button positive">Create an Account</a> <a href="#" class="button">Log In to Account</a></p>

  </section>

</div>
</section>
<?php foot(); ?>
