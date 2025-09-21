import React, { useEffect, useState, useMemo } from "react";
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from "react-native";
import { BASE_URL } from "../../config";

const severityStyles = {
  major: { color: "#fddede", labelColor: "#d9534f" },
  moderate: { color: "#fff9e6", labelColor: "#f0ad4e" },
  minor: { color: "#e6f0ff", labelColor: "#5bc0de" },
};

// ✅ Main Component
// props: visible, onClose, medications, token
const ConfirmResult = ({ visible, onClose, medications, token }) => {
  const [interactionData, setInteractionData] = useState(null);
  const [loadingCheck, setLoadingCheck] = useState(false);
  const [saving, setSaving] = useState(false);

  const medsToUse = useMemo(() => {
    const arr = Array.isArray(medications) ? medications : [];
    const cleaned = arr
      .map((m) => (typeof m === "string" ? m : m?.name || ""))
      .map((s) => (s || "").trim())
      .filter((s) => !!s);
    // unique giữ thứ tự
    return [...new Map(cleaned.map((v) => [v.toLowerCase(), v])).values()];
  }, [medications]);

  // 🔁 Fetch interaction data khi modal mở
  useEffect(() => {
    if (visible) {
      fetchInteractionData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible]);

  const fetchInteractionData = async () => {
    if (!medsToUse.length) {
      setInteractionData(null);
      return;
    }
    try {
      setLoadingCheck(true);

      const res = await fetch(`${BASE_URL}/api/interactions/check`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`, // Bearer <...>
        },
        body: JSON.stringify({
          medications: medsToUse,
          include_user_history: true,
        }),
      });

      const data = await res.json();
      // console.log("🔎 Interaction data:", data);
      // Nếu API trả không chuẩn, vẫn fallback một structure nhẹ để không crash UI
      setInteractionData({
        summary: data?.summary || "Interaction summary is not available.",
        interactions: Array.isArray(data?.interactions)
          ? data.interactions
          : [],
      });
    } catch (error) {
      console.error("❌ Error fetching interaction data:", error);
      setInteractionData({
        summary: "Could not fetch interaction data.",
        interactions: [],
      });
    } finally {
      setLoadingCheck(false);
    }
  };

  // ✅ CONFIRM: vừa SAVE vào /api/prescriptions/save rồi đóng modal
  const handleConfirmSave = async () => {
    if (!medsToUse.length) {
      Alert.alert("Nothing to save", "No valid medication names.");
      return;
    }
    try {
      setSaving(true);

      const res = await fetch(`${BASE_URL}/api/prescriptions/save`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`, // Bearer <...>
        },
        body: JSON.stringify({ medications: medsToUse }),
      });

      const data = await res.json();

      if (!res.ok) {
        // Trả lỗi gọn, không thay đổi UI cũ
        const msg =
          data?.detail ||
          data?.message ||
          "Save failed. Please try again later.";
        Alert.alert("Save failed", msg);
        setSaving(false);
        return;
      }

      // Lưu thành công
      // console.log("✅ Saved:", data);
      Alert.alert("Saved", "Your medications have been saved.");
      setSaving(false);
      onClose && onClose();
    } catch (err) {
      console.error("❌ Save error:", err);
      Alert.alert("Save error", "Cannot connect to the server.");
      setSaving(false);
    }
  };

  return (
    <Modal visible={visible} animationType="slide" transparent={false}>
      <View style={styles.fullscreenContainer}>
        <Text style={styles.header}>Medicine Interaction Warning</Text>

        {/* Loading khi check interactions */}
        {loadingCheck ? (
          <ActivityIndicator size="large" color="#007AFF" />
        ) : (
          <>
            {/* Summary */}
            {interactionData?.summary ? (
              <Text style={styles.summaryText}>{interactionData.summary}</Text>
            ) : (
              <Text style={styles.message}>
                No interaction data available yet.
              </Text>
            )}

            {/* List interactions */}
            <ScrollView style={styles.scroll}>
              {interactionData?.interactions?.map((item, index) => {
                const style =
                  severityStyles[item.severity?.toLowerCase?.() || ""] || {};
                return (
                  <View key={index} style={styles.interactionBox}>
                    {/* Severity Label */}
                    <View
                      style={[
                        styles.levelLabel,
                        { backgroundColor: style.color || "#eee" },
                      ]}
                    >
                      <Text
                        style={[
                          styles.levelText,
                          { color: style.labelColor || "#000" },
                        ]}
                      >
                        {String(item.severity || "unknown")
                          .charAt(0)
                          .toUpperCase() +
                          String(item.severity || "unknown").slice(1)}
                      </Text>
                    </View>

                    {/* Drug Pair */}
                    <Text style={styles.drugs}>
                      {item.drug1_name || "?"} ↔ {item.drug2_name || "?"}
                    </Text>

                    {/* Short Message */}
                    <Text style={styles.message}>
                      {item.description || "No description"}
                    </Text>
                  </View>
                );
              })}
            </ScrollView>

            {/* CONFIRM = SAVE */}
            <TouchableOpacity
              onPress={handleConfirmSave}
              style={[styles.saveBtn, saving && { opacity: 0.7 }]}
              disabled={saving}
            >
              {saving ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <Text style={styles.saveText}>CONFIRM</Text>
              )}
            </TouchableOpacity>

            {/* Close */}
            <TouchableOpacity
              onPress={onClose}
              style={[styles.closeBtn, { marginTop: 10 }]}
              disabled={saving}
            >
              <Text style={styles.closeText}>CLOSE</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </Modal>
  );
};

// ✅ Styles (giữ nguyên layout & tone)
const styles = StyleSheet.create({
  fullscreenContainer: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 20,
    paddingTop: 50,
  },
  header: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 10,
    textAlign: "center",
  },
  summaryText: {
    fontSize: 14,
    color: "#171e24ff",
    marginVertical: 10,
    lineHeight: 20,
    fontWeight: "700",
  },
  scroll: {
    flex: 1,
    marginBottom: 10,
  },
  interactionBox: {
    marginBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: "#ccc",
    paddingBottom: 10,
  },
  levelLabel: {
    alignSelf: "flex-start",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    marginBottom: 5,
  },
  levelText: {
    fontWeight: "bold",
  },
  drugs: {
    fontWeight: "bold",
    fontSize: 16,
    marginBottom: 5,
  },
  message: {
    fontSize: 14,
    color: "#555",
  },
  saveBtn: {
    backgroundColor: "#007AFF",
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: "center",
  },
  saveText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
  closeBtn: {
    backgroundColor: "#f2f2f2",
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: "center",
  },
  closeText: {
    color: "#333",
    fontWeight: "600",
    fontSize: 16,
  },
});

export default ConfirmResult;
