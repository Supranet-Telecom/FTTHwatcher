<template>
  <div v-if="pending" class="flex items-center justify-center h-80">
    <UIcon name="i-heroicons-arrow-path" class="animate-spin size-8 text-primary" />
  </div>

  <div v-else-if="error" class="flex items-center justify-center h-80 text-red-500 gap-2">
    <UIcon name="i-heroicons-exclamation-triangle" class="size-5" />
    <span>Erro ao carregar dados da API.</span>
  </div>

  <div v-else class="h-[420px] w-full">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  pending: boolean
  error: any
}>()
</script>
