attribute vec3 a_position;
attribute vec3 a_normal;

varying vec4 u_eye_pos;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;

// Light and material properties
struct Light {
    vec4 position;
    vec4 diffuse;
    vec4 specular;
    vec4 ambient;
};

uniform Light u_lights[3];  // Light array
varying vec4 v_s[3];
varying vec4 v_h[3];

varying vec4 v_frag_pos;     
varying vec4 v_normal;

void main(void)
{
    // Transform position and normal to world space
    vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
    vec4 normal = vec4(a_normal.x, a_normal.y, a_normal.z, 0.0);
    position = u_model_matrix * position;
    v_normal = normalize(u_model_matrix * normal);

    for(int i = 0; i < 3; i ++)
    {
        v_s[i] = normalize(u_lights[i].position - position);  
        vec4 v = normalize(u_eye_pos - position);             
        v_h[i] = normalize(v_s[i] + v);   

    }
    
    
    gl_Position = u_projection_matrix * u_view_matrix * position;
}