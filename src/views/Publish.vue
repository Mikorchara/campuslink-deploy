<template>
  <div class="publish-page">
    <!-- 顶部导航栏 -->
    <header class="publish-header">
      <button class="nav-btn" aria-label="返回" @click="handleBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
          <path d="M15 19l-7-7 7-7" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <h1 class="header-title">{{ isEdit ? '编辑闲置' : '发布闲置' }}</h1>
      <button v-if="!isEdit" type="button" class="draft-btn" :disabled="uploading || isSubmitting" @click="saveDraft">存草稿</button>
    </header>

    <!-- 滚动表单区域 -->
    <RequestState v-if="initialLoading || loadError" :loading="initialLoading" :error="loadError" @retry="loadExisting" />
    <div v-else class="publish-body">
      <!-- 审核时效提示 -->
      <div class="audit-notice-card">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="sparkle-icon">
          <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span class="audit-text">让闲置流动起来 · 保存成功后即可在闲置列表查看</span>
      </div>

      <!-- 发布成功提示横幅 -->
      <transition name="fade">
        <div v-if="publishedSuccess" class="success-panel" id="successPanel">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="check-icon">
            <circle cx="12" cy="12" r="10" stroke-width="2"/>
            <path d="m9 12 2 2 4-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <div class="success-text-area">
            <h4 class="success-title">保存成功</h4>
            <p class="success-desc">商品已保存，正在前往商品详情。</p>
          </div>
        </div>
      </transition>

      <!-- 1. 商品图片区域 -->
      <section class="form-section" id="secPhotos">
        <div class="section-head">
          <div class="head-left">
            <h2 class="section-title">商品图片</h2>
            <span class="tag-pill">建议实拍</span>
          </div>
          <span class="photo-counter">
            <strong class="count-num">{{ photoList.length }}</strong>/1
          </span>
        </div>

        <!-- 图片网格 -->
        <div class="photo-grid">
          <!-- 已上传图片槽 -->
          <div
            v-for="(photo, index) in photoList"
            :key="index"
            class="photo-slot filled"
            :style="{ background: 'var(--color-bg-subtle)' }"
          >
            <img v-if="photo.url" :src="photo.url" class="photo-img" alt="商品预览" />
            <div v-else class="photo-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="slot-image-icon">
                <rect width="18" height="18" x="3" y="3" rx="2" ry="2" stroke-width="2"/>
                <circle cx="9" cy="9" r="2" stroke-width="2"/>
                <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" stroke-width="2"/>
              </svg>
            </div>
            <span class="slot-label">{{ index === 0 ? '封面图' : `商品图 ${index + 1}` }}</span>
            <button
              type="button"
              class="remove-photo-btn"
              aria-label="删除图片"
              @click="removePhoto(index)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="x-icon">
                <path d="M18 6 6 18" stroke-width="2.5" stroke-linecap="round"/>
                <path d="m6 6 12 12" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <!-- 未填槽位（未达到 8 张时显示） -->
          <div
            v-if="photoList.length < 1"
            class="photo-slot empty"
            @click="triggerFileInput"
          >
            <div class="empty-content">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="plus-icon">
                <line x1="12" y1="5" x2="12" y2="19" stroke-width="2" stroke-linecap="round"/>
                <line x1="5" y1="12" x2="19" y2="12" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <span class="empty-text">添加</span>
            </div>
          </div>

          <!-- 多选快速上传快捷卡片 -->
          <button
            type="button"
            class="multi-add-btn"
            :class="{ disabled: photoList.length >= 1 }"
            :disabled="photoList.length >= 1"
            @click="triggerFileInput"
          >
            <div class="multi-icon-circle">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="multi-icon">
                <path d="M18 22H4a2 2 0 0 1-2-2V6" stroke-width="2" stroke-linecap="round"/>
                <rect width="16" height="16" x="6" y="2" rx="2" stroke-width="2"/>
                <circle cx="12" cy="8" r="2" stroke-width="2"/>
                <path d="m22 14-3.5-3.5a2 2 0 0 0-2.8 0L6 20" stroke-width="2"/>
              </svg>
            </div>
            <span class="multi-text">{{ photoList.length >= 1 ? '已选封面' : '选择封面' }}</span>
          </button>
        </div>

        <!-- 隐藏的原生文件上传 -->
        <input
          ref="fileInputRef"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          class="hidden-file-input"
          @change="onFilesSelected"
        />

        <p class="section-hint">每件商品保存 1 张封面 · JPEG / PNG / WebP，最大 5 MB</p>
        <p v-if="uploading" role="status">正在上传封面，请稍候…</p>
        <p v-if="errors.photos" class="error-text">{{ errors.photos }}</p>
      </section>

      <!-- 2. 商品信息区域 -->
      <section class="form-section" id="secInfo">
        <h2 class="section-title">商品信息</h2>

        <!-- 商品名称 -->
        <div class="field-item">
          <div class="field-label-row">
            <span class="field-label">商品名称</span>
            <span class="char-count">{{ title.length }}/30</span>
          </div>
          <div class="input-wrapper" :class="{ 'has-focus': focusedField === 'title' }">
            <input
              v-model.trim="title"
              type="text"
              maxlength="30"
              class="text-input"
              placeholder="例如：高等数学（第七版）上册 九成新"
              @focus="focusedField = 'title'"
              @blur="focusedField = ''"
              @input="errors.title = ''"
            />
          </div>
          <p v-if="errors.title" class="error-text">{{ errors.title }}</p>
        </div>

        <!-- 商品描述 -->
        <div class="field-item">
          <div class="field-label-row">
            <span class="field-label">商品描述</span>
            <span class="char-count">{{ description.length }}/200</span>
          </div>
          <textarea
            v-model.trim="description"
            rows="4"
            maxlength="200"
            class="textarea-input"
            placeholder="说明成色、购买时间、有无笔记划线、交易地点等，写清楚更容易成交～"
          ></textarea>
        </div>

        <!-- 售价 -->
        <div class="field-item">
          <span class="field-label">售价</span>
          <div class="price-input-wrapper" :class="{ 'has-focus': focusedField === 'price' }">
            <span class="currency-symbol">¥</span>
            <input
              v-model="price"
              type="text"
              inputmode="decimal"
              maxlength="11"
              class="price-input"
              placeholder="0.00"
              @focus="focusedField = 'price'"
              @blur="focusedField = ''"
              @input="onPriceInput"
            />
            <span class="currency-unit">元</span>
          </div>
          <p class="field-hint">参考同款定价，合理价格更容易被秒下</p>
          <p v-if="errors.price" class="error-text">{{ errors.price }}</p>
        </div>
      </section>

      <!-- 3. 商品分类区域 -->
      <section class="form-section" id="secCategory">
        <div class="section-head">
          <h2 class="section-title">商品分类</h2>
          <span class="head-tip">单选</span>
        </div>
        <div class="chip-group">
          <button
            v-for="cat in categories"
            :key="cat"
            type="button"
            class="chip-btn"
            :class="{ active: selectedCategory === cat }"
            @click="selectCategory(cat)"
          >
            {{ cat }}
          </button>
        </div>
        <p v-if="errors.category" class="error-text">{{ errors.category }}</p>
      </section>

      <!-- 4. 交易信息区域 -->
      <section class="form-section" id="secTrade">
        <h2 class="section-title">交易信息</h2>

        <div class="sub-label-row">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="pin-icon">
            <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" stroke-width="2"/>
            <circle cx="12" cy="10" r="3" stroke-width="2"/>
          </svg>
          <span class="field-label">交易校区</span>
        </div>

        <div class="chip-group campus-group">
          <button
            v-for="campus in campusList"
            :key="campus"
            type="button"
            class="campus-chip-btn"
            :class="{ active: selectedCampus === campus }"
            @click="selectedCampus = campus"
          >
            {{ campus }}
          </button>
        </div>

        <label class="field-item">
          <span class="field-label">具体面交地点</span>
          <input v-model.trim="locationDetail" class="text-input" placeholder="如图书馆一楼" maxlength="80" aria-label="具体面交地点" />
        </label>
        <!-- 议价小刀开关 -->
        <div class="switch-row">
          <div class="switch-label-area">
            <p class="switch-title">接受小刀</p>
            <p class="switch-desc">将在商品描述中注明是否接受议价</p>
          </div>
          <button
            type="button"
            role="switch"
            class="toggle-switch"
            :class="{ active: acceptBargain }"
            :aria-checked="acceptBargain"
            @click="acceptBargain = !acceptBargain"
          >
            <span class="toggle-knob"></span>
          </button>
        </div>
      </section>

      <p v-if="submitError" class="error-text" role="alert">{{ submitError }}</p>
      <!-- 校园规范底线说明 -->
      <div class="compliance-footer">
        <p class="compliance-text">
          请勿发布违规、假冒及非校园相关物品<br />
          福帮帮与你一起维护干净的校园交易环境
        </p>
      </div>
    </div>

    <!-- 底部吸底操作栏 -->
    <footer class="publish-footer-bar">
      <button v-if="!isEdit" type="button" class="footer-draft-btn" :disabled="uploading || isSubmitting" @click="saveDraft">存草稿</button>
      <button
        type="button"
        class="footer-submit-btn"
        :class="{ submitted: publishedSuccess }"
        :disabled="isSubmitting || uploading || publishedSuccess || initialLoading || Boolean(loadError)"
        @click="handleSubmit"
      >
        <span v-if="publishedSuccess">已保存</span>
        <span v-else-if="isSubmitting">正在发布...</span>
        <span v-else>{{ isEdit ? '保存修改' : '立即发布' }}</span>
      </button>
    </footer>

    <!-- 全局 Toast -->
    <Teleport to="#app-mobile-frame">
      <div v-if="toastMessage" class="publish-toast">
        {{ toastMessage }}
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { createProduct, updateProduct, getProductDetail, uploadImage, productCategories } from '../api/product';
import { errorMessage } from '../api/request';
import { useUserStore } from '../stores/user';
import RequestState from '../components/common/RequestState.vue';
const router = useRouter();
const route = useRoute();
const session = useUserStore();
const isEdit = computed(() => Boolean(route.params.id));
const fileInputRef = ref<HTMLInputElement | null>(null);
const title = ref('');
const description = ref('');
const price = ref('');
const selectedCategory = ref('');
const selectedCampus = ref('旗山校区');
const locationDetail = ref('');
const acceptBargain = ref(true);
const focusedField = ref('');
const photoList = ref<{ url: string }[]>([]);
const categories = productCategories;
const campusList = ['旗山校区', '铜盘校区', '怡山校区'];
const errors = reactive({ photos: '', title: '', price: '', category: '' });
const isSubmitting = ref(false);
const uploading = ref(false);
const initialLoading = ref(false);
const loadError = ref('');
const submitError = ref('');
const publishedSuccess = ref(false);
const toastMessage = ref('');
let timer: ReturnType<typeof setTimeout>;
function showToastMsg(message: string) { toastMessage.value = message; clearTimeout(timer); timer = setTimeout(() => toastMessage.value = '', 2400); }
function triggerFileInput() { if (!uploading.value && !isSubmitting.value) fileInputRef.value?.click(); }
async function onFilesSelected(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  input.value = '';
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) {
    errors.photos = '请选择 5 MB 以内的 JPEG、PNG 或 WebP 图片'; return;
  }
  uploading.value = true;
  errors.photos = '';
  try { photoList.value = [{ url: await uploadImage(file) }]; }
  catch (error) { errors.photos = errorMessage(error); }
  finally { uploading.value = false; }
}
function removePhoto(index: number) { if (!isSubmitting.value && !uploading.value) photoList.value.splice(index, 1); }
function onPriceInput() { errors.price = ''; }
function selectCategory(category: string) { selectedCategory.value = category; errors.category = ''; }
function handleBack() { void router.push('/idle'); }
const draftKey = computed(() => `campuslink:draft:${session.user?.id}`);
function saveDraft() {
  if (uploading.value || isSubmitting.value) return;
  try {
    localStorage.setItem(draftKey.value, JSON.stringify({ title: title.value, description: description.value, price: price.value,
      category: selectedCategory.value, campus: selectedCampus.value, location: locationDetail.value,
      acceptBargain: acceptBargain.value, image: photoList.value[0]?.url || '' }));
    showToastMsg('草稿已保存到本机，下次发布时可继续编辑');
  } catch { showToastMsg('草稿保存失败，请检查浏览器存储空间'); }
}
async function loadExisting() {
  if (!isEdit.value) return;
  initialLoading.value = true;
  loadError.value = '';
  try {
    const item = await getProductDetail(Number(route.params.id));
    if (item.seller.id !== session.user?.id) throw new Error('只能编辑自己发布的商品');
    title.value = item.title;
    description.value = item.description || '';
    price.value = String(item.price);
    selectedCategory.value = item.category;
    photoList.value = [{ url: item.image_url }];
    selectedCampus.value = campusList.find(campus => item.location?.includes(campus)) || '旗山校区';
    locationDetail.value = (item.location || '').replace(`福州大学${selectedCampus.value}`, '').trim();
    acceptBargain.value = !description.value.includes('不接受议价');
  } catch (error) { loadError.value = errorMessage(error); }
  finally { initialLoading.value = false; }
}
async function handleSubmit() {
  if (isSubmitting.value || uploading.value || publishedSuccess.value) return;
  errors.photos = photoList.value.length ? '' : '请先上传 1 张封面图';
  errors.title = title.value.trim() && title.value.trim().length <= 30 ? '' : '商品名称应为 1–30 字';
  errors.price = /^\d{1,8}(\.\d{1,2})?$/.test(price.value) && Number(price.value) > 0 ? '' : '请输入大于 0、最多两位小数的价格';
  errors.category = productCategories.includes(selectedCategory.value) ? '' : '请选择商品分类';
  if (Object.values(errors).some(Boolean)) { showToastMsg('请完善商品信息后再保存'); return; }
  isSubmitting.value = true;
  submitError.value = '';
  try {
    const cleanDescription = description.value.replace(/\n?是否议价：[接受不]+议价/g, '').trim();
    const payload = {
      title: title.value.trim(), description: `${cleanDescription}\n是否议价：${acceptBargain.value ? '接受议价' : '不接受议价'}`.trim(),
      price: Number(price.value), category: selectedCategory.value, image_url: photoList.value[0].url,
      location: `福州大学${selectedCampus.value} ${locationDetail.value.trim() || '生活区'}`
    };
    const saved = isEdit.value ? await updateProduct(Number(route.params.id), payload) : await createProduct(payload);
    if (!isEdit.value) localStorage.removeItem(draftKey.value);
    publishedSuccess.value = true;
    await router.replace(`/product/${saved.id}`);
  } catch (error) { submitError.value = errorMessage(error); }
  finally { isSubmitting.value = false; }
}
onMounted(async () => {
  if (isEdit.value) { await loadExisting(); return; }
  try {
    const data = JSON.parse(localStorage.getItem(draftKey.value) || 'null');
    if (!data || typeof data !== 'object') return;
    title.value = typeof data.title === 'string' ? data.title : '';
    description.value = typeof data.description === 'string' ? data.description : '';
    price.value = typeof data.price === 'string' ? data.price : '';
    selectedCategory.value = productCategories.includes(data.category) ? data.category : '';
    selectedCampus.value = campusList.includes(data.campus) ? data.campus : '旗山校区';
    locationDetail.value = typeof data.location === 'string' ? data.location : '';
    acceptBargain.value = data.acceptBargain !== false;
    photoList.value = typeof data.image === 'string' && data.image.startsWith('/api/uploads/') ? [{ url: data.image }] : [];
    showToastMsg('已恢复本机草稿');
  } catch { showToastMsg('本机草稿无法读取，请重新填写'); }
});
onUnmounted(() => clearTimeout(timer));
</script>

<style scoped>
.publish-page {
  width: 100%;
  height: 100%;
  background-color: #F5F8F1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 标题栏 */
.publish-header {
  padding-top: 10px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background-color: #F5F8F1;
  border-bottom: 1px solid #E9EEE3;
  flex-shrink: 0;
}

.nav-btn {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1A2119;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.nav-btn:active {
  background-color: #E8F0E1;
}

.nav-icon {
  width: 22px;
  height: 22px;
}

.header-title {
  font-size: 16.5px;
  font-weight: 600;
  color: #141A13;
  margin: 0;
}

.draft-btn {
  font-size: 12.5px;
  color: #6E7A6B;
  padding: 6px 12px;
  border-radius: 999px;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.draft-btn:active {
  background-color: #E8F0E1;
}

/* 滚动表单 */
.publish-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px 16px 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 审核提示 */
.audit-notice-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: linear-gradient(90deg, #EAF9E4 0%, #F7FCF3 100%);
  border: 1px solid #E1F0D8;
  border-radius: 15px;
}

.sparkle-icon {
  width: 16px;
  height: 16px;
  color: #4CB85E;
  flex-shrink: 0;
}

.audit-text {
  font-size: 11.5px;
  color: #5C8A5F;
  line-height: 1.4;
}

/* 成功横幅 */
.success-panel {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  background: #EDF9E7;
  border: 1px solid #CBEAC0;
  border-radius: 16px;
  animation: fadeIn 0.3s ease;
}

.check-icon {
  width: 18px;
  height: 18px;
  color: #3FA852;
  flex-shrink: 0;
  margin-top: 1px;
}

.success-title {
  font-size: 12.5px;
  font-weight: 600;
  color: #2E7B3E;
  margin: 0;
}

.success-desc {
  font-size: 11.5px;
  color: #6F9370;
  margin-top: 3px;
  line-height: 1.4;
}

/* 基础表单块 */
.form-section {
  background: #FFFFFF;
  border-radius: 18px;
  border: 1px solid #EEF2E9;
  padding: 16px;
  box-shadow: 0 8px 20px -16px rgba(24, 60, 30, 0.4);
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.head-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-title {
  font-size: 14.5px;
  font-weight: 600;
  color: #1B231A;
  margin: 0;
}

.tag-pill {
  font-size: 10px;
  font-weight: 500;
  color: #67A96B;
  background: #F1F8EC;
  padding: 2px 6px;
  border-radius: 999px;
}

.photo-counter {
  font-size: 11.5px;
  color: #9AA595;
}

.count-num {
  font-weight: 600;
  color: #4CA45C;
}

.head-tip {
  font-size: 10.5px;
  color: #B3BCAE;
}

/* 图片上传网格 */
.photo-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.photo-slot {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: 12px;
  overflow: hidden;
}

.photo-slot.empty {
  border: 1px dashed #CFDCC7;
  background: #F8FBF5;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s ease;
}

.photo-slot.empty:active {
  background: #EFF7E9;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #A9B5A2;
}

.plus-icon {
  width: 18px;
  height: 18px;
}

.empty-text {
  font-size: 10px;
}

.photo-slot.filled {
  border: 1px solid #E2EADF;
  display: flex;
  align-items: center;
  justify-content: center;
}

.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.85);
}

.slot-image-icon {
  width: 24px;
  height: 24px;
}

.slot-label {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  color: #FFFFFF;
  font-size: 9.5px;
  padding: 2px 6px;
  text-align: center;
}

.remove-photo-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.5);
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.remove-photo-btn:active {
  transform: scale(0.9);
}

.x-icon {
  width: 11px;
  height: 11px;
}

.multi-add-btn {
  aspect-ratio: 1 / 1;
  border-radius: 12px;
  background: #F1FAEA;
  border: 1px solid #CDE6C1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #5FA866;
  cursor: pointer;
  transition: all 0.15s ease;
}

.multi-add-btn:active {
  transform: scale(0.97);
}

.multi-add-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.multi-icon-circle {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: #FFFFFF;
  color: #3FC25A;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px -6px rgba(60, 150, 80, 0.6);
}

.multi-icon {
  width: 16px;
  height: 16px;
}

.multi-text {
  font-size: 10px;
}

.hidden-file-input {
  display: none;
}

.section-hint {
  font-size: 11px;
  color: #A6AFA2;
  margin-top: 10px;
}

/* 字段组 */
.field-item {
  margin-top: 14px;
}

.field-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.field-label {
  font-size: 12.5px;
  font-weight: 500;
  color: #6E776C;
}

.char-count {
  font-size: 10.5px;
  color: #B3BCAE;
}

.input-wrapper {
  height: 46px;
  background: #F7F9F5;
  border: 1px solid #E8EDE3;
  border-radius: 12px;
  padding: 0 14px;
  display: flex;
  align-items: center;
  margin-top: 6px;
  transition: all 0.2s ease;
}

.input-wrapper.has-focus {
  background: #FFFFFF;
  border-color: #9BDD9B;
  box-shadow: 0 0 0 3px rgba(63, 194, 90, 0.15);
}

.text-input {
  width: 100%;
  border: none;
  background: transparent;
  outline: none;
  font-size: 13.5px;
  color: #1A2119;
}

.text-input::placeholder,
.textarea-input::placeholder {
  color: #AFB8AB;
}

.textarea-input {
  width: 100%;
  background: #F7F9F5;
  border: 1px solid #E8EDE3;
  border-radius: 12px;
  padding: 10px 14px;
  margin-top: 6px;
  outline: none;
  font-size: 13.5px;
  line-height: 1.5;
  color: #1A2119;
  resize: none;
  font-family: inherit;
  transition: all 0.2s ease;
}

.textarea-input:focus {
  background: #FFFFFF;
  border-color: #9BDD9B;
  box-shadow: 0 0 0 3px rgba(63, 194, 90, 0.15);
}

.price-input-wrapper {
  height: 46px;
  background: #F7F9F5;
  border: 1px solid #E8EDE3;
  border-radius: 12px;
  padding: 0 14px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  transition: all 0.2s ease;
}

.price-input-wrapper.has-focus {
  background: #FFFFFF;
  border-color: #9BDD9B;
  box-shadow: 0 0 0 3px rgba(63, 194, 90, 0.15);
}

.currency-symbol {
  font-size: 15px;
  font-weight: 600;
  color: #E4574C;
}

.price-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-size: 17px;
  font-weight: 600;
  color: #E4574C;
}

.price-input::placeholder {
  font-weight: normal;
  color: #BFC7BA;
}

.currency-unit {
  font-size: 11.5px;
  color: #A6AFA2;
}

.field-hint {
  font-size: 11px;
  color: #A6AFA2;
  margin-top: 6px;
}

/* 分类 Chips */
.chip-group {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip-btn {
  height: 36px;
  padding: 0 14px;
  border-radius: 999px;
  background: #FFFFFF;
  border: 1px solid #E3EBDE;
  color: #5E6A5B;
  font-size: 12.5px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.chip-btn:active {
  transform: scale(0.95);
}

.chip-btn.active {
  background: #3FC25A;
  border-color: #3FC25A;
  color: #FFFFFF;
  font-weight: 600;
  box-shadow: 0 6px 14px -8px rgba(63, 194, 90, 0.95);
}

/* 交易信息 */
.sub-label-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
}

.pin-icon {
  width: 15px;
  height: 15px;
  color: #9AA595;
}

.campus-group {
  margin-top: 8px;
}

.campus-chip-btn {
  height: 36px;
  padding: 0 14px;
  border-radius: 999px;
  background: #FFFFFF;
  border: 1px solid #E3EBDE;
  color: #5E6A5B;
  font-size: 12.5px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.campus-chip-btn:active {
  transform: scale(0.95);
}

.campus-chip-btn.active {
  background: #F0FAEA;
  border-color: #3FC25A;
  color: #2F8F45;
  font-weight: 600;
}

/* 议价开关 */
.switch-row {
  margin-top: 14px;
  background: #F7FAF4;
  border-radius: 12px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.switch-title {
  font-size: 12.5px;
  font-weight: 500;
  color: #3B473A;
  margin: 0;
}

.switch-desc {
  font-size: 10.5px;
  color: #A0A99C;
  margin-top: 2px;
}

.toggle-switch {
  width: 44px;
  height: 26px;
  border-radius: 999px;
  background: #E1E8DB;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
  border: none;
  flex-shrink: 0;
}

.toggle-switch:active {
  transform: scale(0.95);
}

.toggle-switch.active {
  background: #3FC25A;
}

.toggle-knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  border-radius: 999px;
  background: #FFFFFF;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.toggle-switch.active .toggle-knob {
  transform: translateX(18px);
}

.compliance-footer {
  padding: 16px 20px;
  text-align: center;
}

.compliance-text {
  font-size: 10.5px;
  color: #B3BCAE;
  line-height: 1.5;
}

.error-text {
  color: #D8543F;
  font-size: 11px;
  margin-top: 6px;
}

/* 底部操作栏 */
.publish-footer-bar {
  width: 100%;
  height: 64px;
  flex-shrink: 0;
  background: #FFFFFF;
  border-top: 1px solid #E9EEE3;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  z-index: 10;
  box-sizing: border-box;
}

.footer-draft-btn {
  width: 96px;
  height: 46px;
  border-radius: 999px;
  background: #FFFFFF;
  border: 1px solid #DDE7D7;
  color: #6E7A6B;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.footer-draft-btn:active {
  background: #F5F9F2;
  transform: scale(0.96);
}

.footer-submit-btn {
  flex: 1;
  height: 46px;
  border-radius: 999px;
  background: linear-gradient(135deg, #18C762 0%, #05A843 100%);
  color: #FFFFFF;
  font-size: 15.5px;
  font-weight: 600;
  box-shadow: 0 10px 22px -12px rgba(63, 194, 90, 0.95);
  cursor: pointer;
  transition: transform 0.15s ease, opacity 0.15s ease;
  border: none;
}

.footer-submit-btn:active {
  transform: scale(0.98);
}

.footer-submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.footer-submit-btn.submitted {
  background: #2E7B3E;
}

/* Toast */
.publish-toast {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(31, 42, 29, 0.9);
  color: #FFFFFF;
  padding: 10px 18px;
  border-radius: 999px;
  font-size: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  pointer-events: none;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translate(-50%, 6px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
</style>
