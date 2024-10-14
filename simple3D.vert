attribute vec3 a_position;
attribute vec3 a_normal;

uniform vec4 u_eye_pos;


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
uniform float u_shininess;


void main(void)
{
	vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
	vec4 normal = vec4(a_normal.x, a_normal.y, a_normal.z, 0.0);

	position = u_model_matrix * position;
	normal = normalize(u_model_matrix * normal);

	
	vec4 s = normalize(u_light_position - position);
	vec4 v = normalize(u_eye_pos - position);

	vec4 h = normalize(s+v);
	
	float lambert = max( dot(normal,s), 0.0);
	float phong = max( dot(normal,h), 0.0);

	vec4 ambientColor = u_light_ambient * u_material_ambient;
	vec4 diffuseColor = u_light_diffuse * u_material_diffuse * lambert;
	vec4 specularColor = u_light_specular * u_material_specular * pow(phong, u_shininess);
	vec4 lightCalculatedColor = ambientColor + diffuseColor + specularColor;
	

	v_color =  lightCalculatedColor;
 
	position = u_projection_matrix * (u_view_matrix * position);

	gl_Position = position;
}