<?php
/**
 * Strona główna – złożona wyłącznie z bloków ACF motywu (hero, przewagi,
 * opinie, FAQ, blog). Układ i treść klient ustawia w edytorze strony.
 *
 * @package KawaNaKlik
 */

get_header();

while ( have_posts() ) :
	the_post();
	?>
	<div class="front-blocks">
		<?php the_content(); ?>
	</div>
	<?php
endwhile;

get_footer();
