in vec4 color;
in vec3 position;
in vec4 bone_weights;
in vec4 bone_indices;

uniform mat4 mvp;
uniform mat4 bones[31];

out vec4 fcolor;

int isMatZero(mat4 m);

void main() {
    // bones[0];
    fcolor = color;

    mat4 bone_mat = mat4(0.0);
    for (int i = 0; i < 4; i++) {
        bone_mat += bone_weights[int(bone_indices[i])] * bones[int(bone_indices[i])];
    }

    if (isMatZero(bone_mat) == 1) {
        bone_mat = mat4(1.0);
    }

    vec4 worldPos = bone_mat * vec4(position, 1.0);
    gl_Position = mvp * worldPos;
}

int isMatZero(mat4 m) {
    int result = 1;
    for (int i = 0; i < 4; i++) {
        if (m[i] != vec4(0.0)) {
            result = 0;
            break;
        }
    }
    return result;
}
