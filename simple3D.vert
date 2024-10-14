attribute vec3 a_position;
attribute vec3 a_normal;

uniform vec4 u_eye_pos;
uniform vec4 u_global_ambient;


uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;

varying vec4 v_color;  //Leave the varying variables alone to begin with
uniform vec4 u_light_position;
uniform vec4 u_light_diffuse;
uniform vec4 u_light_specular;
uniform vec4 u_light_ambient;

uniform vec4 u_material_specular;
uniform vec4 u_material_diffuse;
uniform vec4 u_material_ambient;
uniform float shininess;


void main(void)
{
	vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
	vec4 normal = vec4(a_normal.x, a_normal.y, a_normal.z, 0.0);

	position = u_model_matrix * position;
	normal = normalize(u_model_matrix * normal);

	//float light_factor_1 = max(dot(normalize(normal), normalize(vec4(1, 2, 3, 0))), 0.0);
	//float light_factor_2 = max(dot(normalize(normal), normalize(vec4(-3, -2, -1, 0))), 0.0);
	//v_color = (light_factor_1 + light_factor_2) * u_color; // ### --- Change this vector (pure white) to color variable --- #####
	
	vec4 s = normalize(u_light_position - position);
	vec4 v = normalize(u_eye_pos - position);

	vec4 h = normalize(s+v);
	
	float lambert = max( dot(normal,s), 0.0);
	float phong = max( dot(normal,h), 0.0);

	vec4 ambientColor = u_light_ambient * u_material_ambient;
	vec4 diffuseColor = u_light_diffuse * u_material_diffuse * lambert;
	vec4 specularColor = u_light_specular * u_material_specular * pow(phong, shininess);
	vec4 lightCalculatedColor = ambientColor + diffuseColor + specularColor;
	

	v_color =  lightCalculatedColor ;
 
	position = u_projection_matrix * (u_view_matrix * position);

	gl_Position = position;
}