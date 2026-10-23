<?php
/**
 * Błąd 404 – brak strony pod podanym adresem.
 *
 * @package KawaNaKlik
 */

get_header();
?>

<section class="error-404">
	<p class="error-404__code">404</p>
	<h1 class="entry__title"><?php esc_html_e( 'Ups, tej strony nie ma w naszej palarni', 'kawanaklik' ); ?></h1>
	<p><?php esc_html_e( 'Adres mógł się zmienić albo zawiera literówkę. Spróbuj wyszukać to, czego szukasz:', 'kawanaklik' ); ?></p>
	<?php get_search_form(); ?>
	<p><a class="button" href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php esc_html_e( 'Wróć na stronę główną', 'kawanaklik' ); ?></a></p>
</section>

<?php
get_footer();
