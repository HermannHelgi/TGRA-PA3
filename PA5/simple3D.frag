// Interpolated data from vertex shader
varying vec4 v_normal;

uniform sampler2D u_tex01;
uniform sampler2D u_tex02;

uniform float u_using_tex;

struct Light{
    vec4 position;
    vec4 diffuse;
    vec4 specular;
    vec4 ambient;
};

uniform Light u_lights[5];  // Light array
varying vec4 v_s[5];
varying vec4 v_h[5];

varying vec4 u_eye_pos;     // Camera position in world space

uniform vec4 u_material_specular;
uniform vec4 u_material_diffuse;
uniform vec4 u_material_ambient;
uniform float u_shininess;
varying vec2 v_uv;

void main(void)
{
    vec4 mat_diffuse = u_material_diffuse;
    vec4 mat_spec = u_material_specular;
    
    if (u_using_tex == 1.0)
    {
        mat_diffuse *= texture2D(u_tex01, v_uv);
        mat_spec *= texture2D(u_tex02, v_uv);
    }

    // Initialize final color to zero (black)
    vec4 finalColor = vec4(0.0);

    // Loop through each light source and calculate Phong lighting
    for (int i = 0; i < 5; i++) 
    {
    
        float lambert = max(dot(v_normal, (v_s[i])), 0.0);             
        float phong = max(dot(v_normal, (v_h[i])), 0.0);               

        vec4 ambientColor = u_lights[i].ambient * u_material_ambient;
        vec4 diffuseColor = u_lights[i].diffuse * mat_diffuse * lambert;
        vec4 specularColor = u_lights[i].specular * mat_spec * pow(phong, u_shininess);

        finalColor += (ambientColor + diffuseColor + specularColor);
    }

    gl_FragColor = finalColor; // Output final color for the fragment
}
