#version 330 core

// Interpolated data from vertex shader
varying vec3 v_frag_pos;
varying vec3 v_normal;

// Light and material properties
struct Light {
    vec4 position;
    vec4 diffuse;
    vec4 specular;
    vec4 ambient;
};

uniform Light u_lights[5];  // Light array
uniform vec4 u_eye_pos;     // Camera position in world space

uniform vec4 u_material_specular;
uniform vec4 u_material_diffuse;
uniform vec4 u_material_ambient;
uniform float u_shininess;


void main(void)
{
    // Normalize interpolated normal
    vec3 norm = normalize(v_normal);
    
    // Initialize final color to zero (black)
    vec4 finalColor = vec4(0.0);

    // Loop through each light source and calculate Phong lighting
    for (int i = 0; i < 5; i++) {
        // Calculate the light direction, view direction, and halfway vector
        vec3 lightDir = normalize(u_lights[i].position.xyz - v_frag_pos);
        vec3 viewDir = normalize(u_eye_pos.xyz - v_frag_pos);
        vec3 halfwayDir = normalize(lightDir + viewDir);

        // Ambient component
        vec4 ambientColor = u_lights[i].ambient * u_material_ambient;

        // Diffuse component
        float lambert = max(dot(norm, lightDir), 0.0);
        vec4 diffuseColor = u_lights[i].diffuse * u_material_diffuse * lambert;

        // Specular component
        float spec = pow(max(dot(norm, halfwayDir), 0.0), u_shininess);
        vec4 specularColor = u_lights[i].specular * u_material_specular * spec;

        // Accumulate each light's contribution
        finalColor += (ambientColor + diffuseColor + specularColor);
    }

    gl_FragColor = finalColor; // Output final color for the fragment
}
