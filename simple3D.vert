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
	normal = u_model_matrix * normal;

	//float light_factor_1 = max(dot(normalize(normal), normalize(vec4(1, 2, 3, 0))), 0.0);
	//float light_factor_2 = max(dot(normalize(normal), normalize(vec4(-3, -2, -1, 0))), 0.0);
	//v_color = (light_factor_1 + light_factor_2) * u_color; // ### --- Change this vector (pure white) to color variable --- #####
	
	float n_length = length(normal);
	vec4 v = u_eye_pos - position;

	vec4 s = u_light_position - position;
	vec4 h = s+v;
	
	float s_length = length(s);
	float h_length = length(h);
	float lambert = max(0.0,(dot(normal,s)/s_length*n_length));
	float phong = max(0.0,(dot(normal,h)/h_length*n_length));

	vec4 ambientColor = u_light_ambient * u_material_ambient;
	vec4 diffuseColor = u_light_diffuse * u_material_diffuse * lambert;
	vec4 specularColor = u_light_specular * u_material_specular * pow(phong, shininess);
	vec4 lightCalculatedColor = ambientColor + diffuseColor + specularColor;
	

	v_color = u_global_ambient * u_material_diffuse + lightCalculatedColor ;
 
	position = u_projection_matrix * (u_view_matrix * position);

	gl_Position = position;
}