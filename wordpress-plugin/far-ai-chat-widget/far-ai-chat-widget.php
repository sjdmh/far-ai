<?php
/**
 * Plugin Name:       Far AI — Chat Widget
 * Plugin URI:        https://far.agency
 * Description:       ویجت چت هوشمند Far AI برای سایت وردپرسی آژانس فَر. یک دکمه شناور که گفتگوی مشتری را به API فار هوشمند (Far AI) وصل می‌کند.
 * Version:           1.0.0
 * Author:            Far Agency
 * Text Domain:       far-ai-chat-widget
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // دسترسی مستقیم ممنوع
}

define( 'FAR_AI_WIDGET_VERSION', '1.0.0' );
define( 'FAR_AI_WIDGET_DIR', plugin_dir_path( __FILE__ ) );
define( 'FAR_AI_WIDGET_URL', plugin_dir_url( __FILE__ ) );

/* ── تنظیمات پیش‌فرض ─────────────────────────────────────────── */
function far_ai_widget_defaults() {
	return array(
		'api_url'          => 'https://api.far.agency', // آدرس Backend Far AI
		'widget_title'     => 'دستیار فَر',
		'welcome_message'  => 'سلام 👋 من Far AI هستم، دستیار هوشمند آژانس تبلیغاتی فَر — جایی که شکوه تکامل برندت شکل می‌گیره 🦚 چطور می‌تونم کمکت کنم؟',
		'accent_color'     => '#FF7A29', // نارنجی — رنگ دکمه‌ها (سرمه‌ای #0F395B و فیروزه‌ای #40AEAE ثابت هستند)
		'placeholder'      => 'پیام خود را بنویسید...',
		'enable_everywhere' => '1',
	);
}

function far_ai_widget_get_options() {
	$defaults = far_ai_widget_defaults();
	$saved    = get_option( 'far_ai_widget_options', array() );
	return wp_parse_args( $saved, $defaults );
}

/* ── صفحه تنظیمات ────────────────────────────────────────────── */
add_action( 'admin_menu', 'far_ai_widget_menu' );
function far_ai_widget_menu() {
	add_options_page(
		__( 'Far AI Chat Widget', 'far-ai-chat-widget' ),
		__( 'Far AI Widget', 'far-ai-chat-widget' ),
		'manage_options',
		'far-ai-chat-widget',
		'far_ai_widget_settings_page'
	);
}

add_action( 'admin_init', 'far_ai_widget_register_settings' );
function far_ai_widget_register_settings() {
	register_setting( 'far_ai_widget_group', 'far_ai_widget_options', 'far_ai_widget_sanitize' );
}

function far_ai_widget_sanitize( $input ) {
	$defaults = far_ai_widget_defaults();
	$clean    = array();

	$clean['api_url']           = esc_url_raw( isset( $input['api_url'] ) ? $input['api_url'] : $defaults['api_url'] );
	$clean['widget_title']      = sanitize_text_field( isset( $input['widget_title'] ) ? $input['widget_title'] : $defaults['widget_title'] );
	$clean['welcome_message']   = sanitize_textarea_field( isset( $input['welcome_message'] ) ? $input['welcome_message'] : $defaults['welcome_message'] );
	$clean['accent_color']      = sanitize_hex_color( isset( $input['accent_color'] ) ? $input['accent_color'] : $defaults['accent_color'] );
	$clean['placeholder']       = sanitize_text_field( isset( $input['placeholder'] ) ? $input['placeholder'] : $defaults['placeholder'] );
	$clean['enable_everywhere'] = isset( $input['enable_everywhere'] ) ? '1' : '0';

	return $clean;
}

function far_ai_widget_settings_page() {
	$options = far_ai_widget_get_options();
	?>
	<div class="wrap">
		<h1>🤖 Far AI — Chat Widget</h1>
		<p>ویجت چت را به API فار هوشمند وصل کنید. برای نمایش فقط در یک صفحه از شورت‌کد <code>[far_ai_chat]</code> استفاده کنید.</p>
		<form method="post" action="options.php">
			<?php settings_fields( 'far_ai_widget_group' ); ?>
			<table class="form-table" role="presentation">
				<tr>
					<th scope="row"><label for="far_api_url">آدرس API</label></th>
					<td>
						<input type="url" id="far_api_url" name="far_ai_widget_options[api_url]" value="<?php echo esc_attr( $options['api_url'] ); ?>" class="regular-text" placeholder="https://api.far.agency" />
						<p class="description">آدرس سرور Far AI — مثل <code>https://api.far.agency</code> (بدون اسلش انتهایی).</p>
					</td>
				</tr>
				<tr>
					<th scope="row"><label for="far_widget_title">عنوان ویجت</label></th>
					<td><input type="text" id="far_widget_title" name="far_ai_widget_options[widget_title]" value="<?php echo esc_attr( $options['widget_title'] ); ?>" class="regular-text" /></td>
				</tr>
				<tr>
					<th scope="row"><label for="far_welcome_message">پیام خوش‌آمد</label></th>
					<td><textarea id="far_welcome_message" name="far_ai_widget_options[welcome_message]" class="large-text" rows="2"><?php echo esc_textarea( $options['welcome_message'] ); ?></textarea></td>
				</tr>
				<tr>
					<th scope="row"><label for="far_accent_color">رنگ اصلی</label></th>
					<td><input type="text" id="far_accent_color" name="far_ai_widget_options[accent_color]" value="<?php echo esc_attr( $options['accent_color'] ); ?>" class="regular-text" /></td>
				</tr>
				<tr>
					<th scope="row"><label for="far_placeholder">متن راهنما</label></th>
					<td><input type="text" id="far_placeholder" name="far_ai_widget_options[placeholder]" value="<?php echo esc_attr( $options['placeholder'] ); ?>" class="regular-text" /></td>
				</tr>
				<tr>
					<th scope="row">نمایش در همه صفحات</th>
					<td>
						<label>
							<input type="checkbox" name="far_ai_widget_options[enable_everywhere]" value="1" <?php checked( $options['enable_everywhere'], '1' ); ?> />
							فعال‌سازی خودکار در تمام صفحات سایت
						</label>
						<p class="description">اگر غیرفعال باشد، فقط با شورت‌کد <code>[far_ai_chat]</code> نمایش داده می‌شود.</p>
					</td>
				</tr>
			</table>
			<?php submit_button(); ?>
		</form>
	</div>
	<?php
}

/* ── بارگذاری اسکریپت‌ها و استایل‌ها ─────────────────────────── */
add_action( 'wp_enqueue_scripts', 'far_ai_widget_enqueue' );
function far_ai_widget_enqueue() {
	$options  = far_ai_widget_get_options();
	$show_now = ( '1' === $options['enable_everywhere'] ) || has_shortcode( get_post_field( 'post_content' ), 'far_ai_chat' );

	if ( ! $show_now ) {
		return;
	}

	wp_enqueue_style( 'far-ai-widget', FAR_AI_WIDGET_URL . 'assets/css/far-ai-widget.css', array(), FAR_AI_WIDGET_VERSION );
	wp_enqueue_script( 'far-ai-widget', FAR_AI_WIDGET_URL . 'assets/js/far-ai-widget.js', array(), FAR_AI_WIDGET_VERSION, true );

	wp_localize_script(
		'far-ai-widget',
		'FarAIConfig',
		array(
			'apiUrl'         => untrailingslashit( $options['api_url'] ) . '/api/chat',
			'widgetTitle'    => $options['widget_title'],
			'welcomeMessage' => $options['welcome_message'],
			'accentColor'    => $options['accent_color'],
			'placeholder'    => $options['placeholder'],
		)
	);
}

/* ── خروجی بدنه ویجت ────────────────────────────────────────── */
add_action( 'wp_footer', 'far_ai_widget_footer' );
function far_ai_widget_footer() {
	$options = far_ai_widget_get_options();
	if ( '1' !== $options['enable_everywhere'] ) {
		return;
	}
	echo '<div id="far-ai-widget-root"></div>';
}

/* ── شورت‌کد ────────────────────────────────────────────────── */
add_shortcode( 'far_ai_chat', 'far_ai_widget_shortcode' );
function far_ai_widget_shortcode() {
	return '<div id="far-ai-widget-root"></div>';
}
